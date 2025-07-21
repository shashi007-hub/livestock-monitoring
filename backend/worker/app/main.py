from dotenv import load_dotenv
load_dotenv()

import os
import time
import queue
import json
import uuid
from concurrent.futures import ProcessPoolExecutor
import paho.mqtt.client as mqtt
from app.distributed_worker import DistributedWorker
from app.database.db import init_db
from threading import Lock
import base64

# Add parent directory to sys.path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.logging_service import MultiprocessLogger

# Configure logger
logger = MultiprocessLogger.get_logger("MainApp")

MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_MIC = os.getenv("MQTT_TOPIC_MIC", "inference/microphone")
MQTT_TOPIC_ACC= os.getenv("MQTT_TOPIC_ACC", "inference/accelerometer")
MQTT_TOPIC_CAMERA = os.getenv("MQTT_TOPIC_CAMERA", "inference/camera")
IS_DISTRIBUTED = False
CHUNK_SIZE = None

BATCH_TIMEOUT = 500
# mic_request_count = 0
mic_batch_state = {}  # {bovine_id: {"is_started": False, "data_count": 0}}

BATCH_THRESHOLDS = {
    "inference/microphone": 1,  
    "inference/accelerometer": 20,
    "inference/camera": 1
}

WORKER_ID = str(uuid.uuid4())

class ThreadSafeQueueManager:
    def __init__(self):
        self.queues = {}
        self.lock = Lock()
        self.last_process_times = {}
        self.mic_batches = {}  # {(bovine_id): {"start": msg, "chunks": [], "ended": False}}

    def get_or_create_queue(self, topic, bovine_id):
        key = (topic, bovine_id)
        with self.lock:
            if key not in self.queues:
                self.queues[key] = queue.Queue()
                self.last_process_times[key] = time.time()
            return self.queues[key]

    def get_last_process_time(self, topic, bovine_id):
        with self.lock:
            return self.last_process_times.get((topic, bovine_id), time.time())

    def update_last_process_time(self, topic, bovine_id):
        with self.lock:
            self.last_process_times[(topic, bovine_id)] = time.time()

    def get_all_queues(self):
        with self.lock:
            return list(self.queues.items())

queue_manager = ThreadSafeQueueManager()

def   run_inference_and_publish(messages):
    """
    Process Function: This runs in a separate process from the main process.
    Each call creates a new process from the ProcessPoolExecutor.
    """
    try:
        from app.mapping import microphone_pipeline, accelerometer_pipeline, camera_pipeline
    except Exception as e:
        print(f"Import error: {e}")

    
    if not messages:
        return None
    
    logger.info(f"[{WORKER_ID}] Collected {len(messages)} messages for processing")
    # print(messages)
        
    # All messages in a batch should have the same topic and bovine_id
    topic = messages[0]["topic"]
    bovine_id = messages[0]["bovine_id"]
    
    
    # Create a batch message with all data points
    batch_message = {
            "topic": topic,
            "bovine_id": bovine_id,
            "batch_size": len(messages),
            "timestamp": time.time(),
            "data": messages
    }
        
        # Process the batch through the pipeline
   
    logger.info(f"[{WORKER_ID}] Processing batch of {len(messages)} messages for bovine {bovine_id} on topic {topic}")
    
    if(topic == "inference/microphone"):
        result = microphone_pipeline(batch_message)
    elif(topic == "inference/accelerometer"):
        result = accelerometer_pipeline(batch_message)
    elif(topic == "inference/camera"):
        result = camera_pipeline(batch_message)
        logger.info(f"[{WORKER_ID}] Processed batch of {len(messages)} messages for bovine {bovine_id} on topic {topic}")
    
    return result

def on_message(client, userdata, msg):
    try:
        message = json.loads(msg.payload.decode())
        if not isinstance(message, dict):
            logger.error(f"[{WORKER_ID}] Error: Decoded message is not a dictionary: {message}")
            return
        topic = msg.topic
        message["topic"] = topic

        if topic == MQTT_TOPIC_MIC:
            bovine_id = message.get("bovine_id")
            msg_type = message.get("type")

            if bovine_id is None:
                logger.error(f"[{WORKER_ID}] Error: Message missing bovine_id field")
                return

            # Initialize state if not present
            if bovine_id not in mic_batch_state:
                mic_batch_state[bovine_id] = {"is_started": False, "data_count": 0, "data": [],"start_at": None,"chunk_size":0}

            state = mic_batch_state[bovine_id]

            if msg_type == "start":
                if "chunks" in message:
                    state["chunk_size"] =  message["chunks"]
                    chunk = state["chunk_size"] 
                    logger.info(f"[{WORKER_ID}] CHUNK_SIZE set to {chunk } for bovine {bovine_id}")
                else:
                    logger.warning(f"[{WORKER_ID}] WARNING: Start message for bovine {bovine_id} missing or invalid 'chunks'. Discarding batch.")
                    state["is_started"] = False
                    state["data"] = []
                    state["data_count"] = 0
                    state["chunk_size"]=0
                    return
                if state["is_started"]:
                    logger.warning(f"[{WORKER_ID}] WARNING: Received start before previous end for bovine {bovine_id}. Clearing batch.")
                    state["data"] = []
                    state["data_count"] = 0
                state["is_started"] = True
                state["data"] = []
                state["data_count"] = 0
                state["start_at"] = message["timestamp"]
                logger.info(f"[{WORKER_ID}] Start received for bovine {bovine_id}")

            elif msg_type == "data":
                if not state["is_started"]:
                    logger.warning(f"[{WORKER_ID}] WARNING: Data received before start for bovine {bovine_id}. Ignoring.")
                    return
                # Store both index and data for sorting later
                state["data"].append({"index": message["index"], "data": message["data"]})
                logger.info(f"[{WORKER_ID}] Data received for bovine {bovine_id}. Total data count: {state['data_count'] + 1}")
                state["data_count"] += 1
                if state["data_count"] > state["chunk_size"] :
                    logger.warning(f"[{WORKER_ID}] WARNING: More than chunk_size data messages for bovine {bovine_id}. Clearing batch.")
                    state["is_started"] = False
                    state["data"] = []
                    state["data_count"] = 0

            elif msg_type == "end":
                if not state["is_started"]:
                    logger.warning(f"[{WORKER_ID}] WARNING: End received before start for bovine {bovine_id}. Ignoring.")
                    return
                if state["data_count"] == state["chunk_size"] :
                    logger.info(f"[{WORKER_ID}] End received for bovine {bovine_id}. Preparing to queue batch.")
                    joined_audio = b''.join(
                        base64.b64decode(item["data"]) for item in sorted(state["data"], key=lambda x: x["index"])
                    )
                    # print("item _data", state["data")
                    batch = {
                        "topic": topic,
                        "bovine_id": bovine_id,
                        "batch_size": state["data_count"],
                        "timestamp": state["start_at"],
                        "data": joined_audio
                    }
                    q = queue_manager.get_or_create_queue(topic, bovine_id)
                    q.put(batch)
                    logger.info(f"[{WORKER_ID}] Valid batch queued for bovine {bovine_id}")
                else:
                    logger.warning(f"[{WORKER_ID}] WARNING: Invalid batch for bovine {bovine_id}: expected chunk_size data, got {state['data_count']}. Clearing batch.")
                # Reset state
                state["is_started"] = False
                state["data"] = []
                state["data_count"] = 0

            else:
                logger.warning(f"[{WORKER_ID}] WARNING: Unknown message type '{msg_type}' for bovine {bovine_id}")

        # Handle other topics as before...
        elif topic in [MQTT_TOPIC_ACC, MQTT_TOPIC_CAMERA]:
            bovine_id = message.get("bovine_id")
            if bovine_id is None:
                logger.error(f"[{WORKER_ID}] Error: Message missing bovine_id field")
                return
            
            q = queue_manager.get_or_create_queue(topic, bovine_id)
            q.put(message)
            # logger.info(f"[{WORKER_ID}] Queued message from {topic} for bovine {bovine_id}")

        else:
            logger.error(f"[{WORKER_ID}] Error: Unknown topic {topic}")

    except json.JSONDecodeError:
        logger.error(f"[{WORKER_ID}] Error: Invalid JSON message")
    except Exception as e:
        logger.error(f"[{WORKER_ID}] Error processing message: {str(e)}")

def mqtt_subscribe():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT,clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY)
    client.subscribe([(MQTT_TOPIC_MIC, 0), (MQTT_TOPIC_ACC, 0), (MQTT_TOPIC_CAMERA, 0)])
    client.loop_start()
    return client

def main():
    logger.info(f"[{WORKER_ID}] Starting MQTT worker (distributed={IS_DISTRIBUTED})")
    init_db()

    if IS_DISTRIBUTED:
        worker = DistributedWorker()
        worker.start()
    else:
        client = mqtt_subscribe()
        with ProcessPoolExecutor(max_workers=3) as executor:
            while True:
                try:
                    for (topic, bovine_id), q in queue_manager.get_all_queues():
                        curr_time = time.time()
                        last_process_time = queue_manager.get_last_process_time(topic, bovine_id)

                        should_process = (
                            not q.empty() and
                            (q.qsize() >= BATCH_THRESHOLDS[topic] or 
                             curr_time - last_process_time >= BATCH_TIMEOUT)
                        )

                        if should_process:
                            logger.info(f"[{WORKER_ID}] Triggering batch process for topic {topic}, bovine {bovine_id}")
                            messages = []
                            try:
                                while not q.empty():
                                    message = q.get_nowait()
                                    messages.append(message)
                                    q.task_done()
                            except queue.Empty:
                                pass

                            executor.submit(run_inference_and_publish, messages)
                            queue_manager.update_last_process_time(topic, bovine_id)

                except Exception as e:
                    logger.error(f"[{WORKER_ID}] Main loop error: {str(e)}", exc_info=True)

                time.sleep(1)

if __name__ == "__main__":
    main()
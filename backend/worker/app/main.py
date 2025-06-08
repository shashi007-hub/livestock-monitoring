from dotenv import load_dotenv
load_dotenv()

import os
import time
import logging
from threading import Lock
import queue
import json
import uuid
from concurrent.futures import ProcessPoolExecutor
import paho.mqtt.client as mqtt
from app.distributed_worker import DistributedWorker
from app.database.db import init_db

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')

MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_MIC = os.getenv("MQTT_TOPIC_MIC", "inference/microphone")
MQTT_TOPIC_ACC= os.getenv("MQTT_TOPIC_ACC", "inference/accelerometer")
MQTT_TOPIC_CAMERA = os.getenv("MQTT_TOPIC_CAMERA", "inference/camera")
IS_DISTRIBUTED = False

BATCH_TIMEOUT = 500
mic_request_count = 0


BATCH_THRESHOLDS = {
    "inference/microphone": 1,  # 220 + 2 for start/end messages
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
    
    print(f"[{WORKER_ID}] Collected {len(messages)} messages for processing")
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
   
    print(f"[{WORKER_ID}] Processing batch of {len(messages)} messages for bovine {bovine_id} on topic {topic}")
    
    if(topic == "inference/microphone"):
        result = microphone_pipeline(batch_message)
    elif(topic == "inference/accelerometer"):
        result = accelerometer_pipeline(batch_message)
    elif(topic == "inference/camera"):
        result = camera_pipeline(batch_message)
        print(result)
        print(f"[{WORKER_ID}] Processed batch of {len(messages)} messages for bovine {bovine_id} on topic {topic}")
    
    return result

def on_message(client, userdata, msg):
    global mic_request_count
    try:
        message = json.loads(msg.payload.decode())
        topic = msg.topic
        message["topic"] = topic

        if "bovine_id" not in message:
            logging.warning(f"[{WORKER_ID}] Message missing bovine_id field")
            return

        bovine_id = message["bovine_id"]

        if topic == MQTT_TOPIC_MIC:
            mic_request_count += 1
            logging.info(f"[{WORKER_ID}] Microphone topic request count: {mic_request_count}")

            mic_state = queue_manager.mic_batches.get(bovine_id, {"start": None, "chunks": [], "ended": False})
            msg_type = message.get("type")

            if msg_type == "start":
                if mic_state["start"] is not None and not mic_state["ended"]:
                    logging.warning(f"[{WORKER_ID}] New start before end. Discarding previous batch for {bovine_id}.")
                mic_state = {"start": message, "chunks": [], "ended": False}
                logging.info(f"[{WORKER_ID}] Received start for {bovine_id}")

            elif msg_type == "data":
               
                if mic_state["start"] is not None and not mic_state["ended"]:
                    # mic_state["chunks"].extend(message.get("data", []))
                    mic_state["chunks"].append(message.get("data", ""))
                    # with open("mic_chunks_debug.txt", "a") as f:
                    #     f.write(f"{mic_state['chunks']}\n")
                    logging.debug(f"[{WORKER_ID}] Received data chunk for {bovine_id}. Total: {len(mic_state['chunks'])}")
                else:
                    logging.warning(f"[{WORKER_ID}] Data received without start or after end for {bovine_id}. Ignored.")

            elif msg_type == "end":
                if mic_state["start"] is not None and not mic_state["ended"]:
                    mic_state["ended"] = True
                    
                    if len(mic_state["chunks"]) == 220:
                        mic_message = {
                            "bovine_id": bovine_id,
                            "audio_raw": mic_state["chunks"],
                            "probability": 0.9,
                            "timestamp": mic_state["start"]["timestamp"],
                            "topic": topic
                        }
                        logging.info(f"[{WORKER_ID}] Finalizing valid batch for {bovine_id} with 220 chunks.")
                        # run_inference_and_publish([mic_message])
                        q = queue_manager.get_or_create_queue(topic, bovine_id)
                        q.put(mic_message)
                    else:
                        logging.warning(f"[{WORKER_ID}] Invalid batch for {bovine_id}: expected 220 chunks, got {len(mic_state['chunks'])}")
                    mic_state = {"start": None, "chunks": [], "ended": False}

            queue_manager.mic_batches[bovine_id] = mic_state

        elif topic in [MQTT_TOPIC_ACC, MQTT_TOPIC_CAMERA]:
            q = queue_manager.get_or_create_queue(topic, bovine_id)
            q.put(message)
            logging.debug(f"[{WORKER_ID}] Queued {topic} message for bovine {bovine_id}")

    except json.JSONDecodeError:
        logging.error(f"[{WORKER_ID}] Invalid JSON message")
    except Exception as e:
        logging.error(f"[{WORKER_ID}] Error processing message: {str(e)}")

def mqtt_subscribe():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.subscribe([(MQTT_TOPIC_MIC, 0), (MQTT_TOPIC_ACC, 0), (MQTT_TOPIC_CAMERA, 0)])
    client.loop_start()
    return client

def main():
    logging.info(f"[{WORKER_ID}] Starting MQTT worker (distributed={IS_DISTRIBUTED})")
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
                            logging.info(f"[{WORKER_ID}] Triggering batch process for topic {topic}, bovine {bovine_id}")
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
                    logging.error(f"[{WORKER_ID}] Main loop error: {str(e)}")

                time.sleep(1)

if __name__ == "__main__":
    main()

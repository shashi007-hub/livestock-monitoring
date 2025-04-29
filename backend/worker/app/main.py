from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import os
import time
from threading import Lock
import queue
import json
import uuid
from concurrent.futures import ProcessPoolExecutor
import paho.mqtt.client as mqtt
from app.distributed_worker import DistributedWorker
from app.database.db import init_db

MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_MIC = os.getenv("MQTT_TOPIC_MIC", "inference/microphone")
MQTT_TOPIC_ACC= os.getenv("MQTT_TOPIC_ACC", "inference/accelerometer")
MQTT_TOPIC_CAMERA = os.getenv("MQTT_TOPIC_CAMERA", "inference/camera")
IS_DISTRIBUTED = False  # Set to True for distributed mode, False for local mode

# Define threshold for batch processing
BATCH_THRESHOLD = 3  # Process messages when queue reaches this size for a specific bovine
BATCH_TIMEOUT = 200  # Seconds to wait before processing incomplete batch

BATCH_THRESHOLDS = {
    "inference/microphone": 3,
    "inference/accelerometer": 1800,
    "inference/camera": 10
}

WORKER_ID = str(uuid.uuid4())

class ThreadSafeQueueManager:
    """Thread-safe queue manager for handling messages by topic and bovine_id"""
    def __init__(self):
        self.queues = {}  # {(topic, bovine_id): Queue()}
        self.lock = Lock()
        self.last_process_times = {}  # {(topic, bovine_id): timestamp}
        
    def get_or_create_queue(self, topic, bovine_id):
        """Thread-safe method to get or create a queue for a topic-bovine pair"""
        key = (topic, bovine_id)
        with self.lock:
            if key not in self.queues:
                self.queues[key] = queue.Queue()
                self.last_process_times[key] = time.time()
            return self.queues[key]
            
    def get_last_process_time(self, topic, bovine_id):
        """Thread-safe method to get last process time"""
        with self.lock:
            return self.last_process_times.get((topic, bovine_id), time.time())
            
    def update_last_process_time(self, topic, bovine_id):
        """Thread-safe method to update last process time"""
        with self.lock:
            self.last_process_times[(topic, bovine_id)] = time.time()
            
    def get_all_queues(self):
        """Thread-safe method to get all queues"""
        with self.lock:
            return list(self.queues.items())

# Global queue manager instance
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
    print(messages)
        
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
        print(f"[{WORKER_ID}] Processed batch of {len(messages)} messages for bovine {bovine_id} on topic {topic}")
    
    return result
    

def on_message(client, userdata, msg):
    """
    Callback Function: Runs in the MQTT client's thread.
    This is separate from the main thread and process workers.
    """
    try:
        message = json.loads(msg.payload.decode())
        if "bovine_id" not in message:
            print(f"[{WORKER_ID}] Error: Message missing bovine_id field")
            return
            
        message["topic"] = msg.topic  # Add topic to message for processing
        bovine_id = message["bovine_id"]
        
        if msg.topic not in [MQTT_TOPIC_MIC, MQTT_TOPIC_ACC, MQTT_TOPIC_CAMERA]:
            print(f"[{WORKER_ID}] Error: Unknown topic {msg.topic}")
            return
            
        # Get or create queue in thread-safe manner
        q = queue_manager.get_or_create_queue(msg.topic, bovine_id)
        q.put(message)
        print(f"[{WORKER_ID}] Queued message from {msg.topic} for bovine {bovine_id}")
        
    except json.JSONDecodeError:
        print(f"[{WORKER_ID}] Error: Invalid JSON message")
    except Exception as e:
        print(f"[{WORKER_ID}] Error processing message: {str(e)}")

def mqtt_subscribe():
    """
    Creates MQTT client in the main thread, but client.loop_start()
    creates a separate thread for MQTT operations
    """
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.subscribe([(MQTT_TOPIC_MIC, 0), (MQTT_TOPIC_ACC, 0), (MQTT_TOPIC_CAMERA, 0)])
    client.loop_start()
    return client
    

def main():
    """
    Main Process: Initializes components and manages the main processing loop
    - MQTT client runs in a separate thread (created by client.loop_start())
    - ProcessPoolExecutor creates separate processes for inference
    - Main loop runs in the main thread
    """
    print(f"[{WORKER_ID}] Starting MQTT worker (distributed={IS_DISTRIBUTED})")
    
    # Initialize the database
    print(f"[{WORKER_ID}] Initializing database...")
    init_db()
    
    if IS_DISTRIBUTED:
        worker = DistributedWorker()
        worker.start()
    else:
        client = mqtt_subscribe()
        with ProcessPoolExecutor(max_workers=3) as executor:
            while True:
                try:
                    # Iterate through all queues in a thread-safe manner
                    for (topic, bovine_id), q in queue_manager.get_all_queues():
                        curr_time = time.time()
                        last_process_time = queue_manager.get_last_process_time(topic, bovine_id)
                        
                        should_process = (
                            not q.empty() and 
                            (q.qsize() >= BATCH_THRESHOLD or 
                            curr_time - last_process_time >= BATCH_TIMEOUT)
                        )
                        
                        if should_process:
                            print(f"[{WORKER_ID}] Processing messages from topic: {topic}, bovine_id: {bovine_id}")
                            print(f"[{WORKER_ID}] Queue size: {q.qsize()}, Time since last process: {curr_time - last_process_time:.2f}s")
                            messages = [] # (particular sensor for a particular cow)
                            try:
                                while len(messages) < BATCH_THRESHOLD and not q.empty():
                                    message = q.get_nowait()
                                    messages.append(message)
                                    q.task_done()
                            except queue.Empty:
                                pass
                            future = executor.submit(run_inference_and_publish, messages)
                            queue_manager.update_last_process_time(topic, bovine_id)
                                
                except Exception as e:
                    print(f"[{WORKER_ID}] Error in main loop: {str(e)}")
                    continue

                time.sleep(1)  # Prevent busy-waiting

if __name__ == "__main__":
    main()



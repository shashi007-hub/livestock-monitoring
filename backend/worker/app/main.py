from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import os
import time
from collections import defaultdict
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
BATCH_THRESHOLD = 5  # Process messages when queue reaches this size for a specific bovine
BATCH_TIMEOUT = 30  # Seconds to wait before processing incomplete batch

WORKER_ID = str(uuid.uuid4())

# Nested queue structure: topic -> bovine_id -> queue
topic_queues = {
    MQTT_TOPIC_MIC: defaultdict(queue.Queue),
    MQTT_TOPIC_ACC: defaultdict(queue.Queue),
    MQTT_TOPIC_CAMERA: defaultdict(queue.Queue)
}

# Track last process time for each topic and bovine
last_process_time = defaultdict(lambda: defaultdict(lambda: time.time()))

# PLEASE NOTE ALL THIS FUNCTION WILL BE RUNNING IN A PARALLEL PROCXESS 
# HENCE ITS BETTER TO JUST IMPORT INSIDE FUNCTIONS AND **NOT HAVE GLOBAL SCOPE** TO MAKE SURE THERE ARE NO LOCK ISSUES
def run_inference_and_publish(topic_queue):
    from app.mapping import topic_to_pipeline
    
    # Collect all messages in the queue up to threshold
    messages = []
    bovine_id = None
    
    try:
        while len(messages) < BATCH_THRESHOLD and not topic_queue.empty():
            msg = topic_queue.get_nowait()
            # For the first message, set the bovine_id
            if not messages:
                bovine_id = msg["bovine_id"]
            # Only add messages from the same bovine to this batch
            if msg["bovine_id"] == bovine_id:
                messages.append(msg)
            else:
                # Put back message from different bovine
                topic_queue.put(msg)
    except queue.Empty:
        pass
    
    if not messages:
        return None
        
    # All messages in a batch should have the same topic and bovine_id
    topic = messages[0]["topic"]
    pipeline = topic_to_pipeline[topic]    
    if pipeline:
        # Create a batch message with all data points
        batch_message = {
            "topic": topic,
            "bovine_id": bovine_id,
            "batch_size": len(messages),
            "timestamp": time.time(),
            "data": messages
        }
        
        # Process the batch through the pipeline
        result = pipeline(batch_message)
        print(f"[{WORKER_ID}] Processed batch of {len(messages)} messages for bovine {bovine_id} on topic {topic}")
        return result
    
    return None

def on_message(client, userdata, msg):
    try:
        message = json.loads(msg.payload.decode())
        if "bovine_id" not in message:
            print(f"[{WORKER_ID}] Error: Message missing bovine_id field")
            return
            
        message["topic"] = msg.topic  # Add topic to message for processing
        bovine_id = message["bovine_id"]
        
        if msg.topic not in topic_queues:
            print(f"[{WORKER_ID}] Error: Unknown topic {msg.topic}")
            return
            
        # Add message to appropriate queue based on both topic and bovine_id
        topic_queues[msg.topic][bovine_id].put(message)
        print(f"[{WORKER_ID}] Queued message from {msg.topic} for bovine {bovine_id}")
        
    except json.JSONDecodeError:
        print(f"[{WORKER_ID}] Error: Invalid JSON message")
    except Exception as e:
        print(f"[{WORKER_ID}] Error processing message: {str(e)}")

def mqtt_subscribe():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.subscribe([(MQTT_TOPIC_MIC, 0), (MQTT_TOPIC_ACC, 0), (MQTT_TOPIC_CAMERA, 0)])
    client.loop_start()
    return client

def main():
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
                    # Iterate through all topics
                    for topic, bovine_queues in topic_queues.items():
                        # For each topic, check all bovine queues
                        for bovine_id, q in bovine_queues.items():
                            curr_time = time.time()
                            should_process = (
                                not q.empty() and 
                                (q.qsize() >= BATCH_THRESHOLD or 
                                curr_time - last_process_time[topic][bovine_id] >= BATCH_TIMEOUT)
                            )
                            
                            if should_process:
                                print(f"[{WORKER_ID}] Processing messages from topic: {topic}, bovine_id: {bovine_id}")
                                print(f"[{WORKER_ID}] Queue size: {q.qsize()}, Time since last process: {curr_time - last_process_time[topic][bovine_id]:.2f}s")
                                future = executor.submit(run_inference_and_publish, q)
                                last_process_time[topic][bovine_id] = curr_time
                                
                except Exception as e:
                    print(f"[{WORKER_ID}] Error in main loop: {str(e)}")
                    continue

                # Small sleep to prevent CPU spinning
                time.sleep(0.1)

if __name__ == "__main__":
    main()

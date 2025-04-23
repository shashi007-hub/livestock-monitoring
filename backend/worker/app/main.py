import os
import time
import queue
import json
import uuid
from concurrent.futures import ProcessPoolExecutor
import paho.mqtt.client as mqtt
from distributed_worker import DistributedWorker
from database.db import init_db

MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_MIC = os.getenv("MQTT_TOPIC_MIC", "inference/microphone")
MQTT_TOPIC_ACC= os.getenv("MQTT_TOPIC_ACC", "inference/accelerometer")
MQTT_TOPIC_CAMERA = os.getenv("MQTT_TOPIC_CAMERA", "inference/camera")
IS_DISTRIBUTED = False  # Set to True for distributed mode, False for local mode

# Define threshold for batch processing
BATCH_THRESHOLD = 5  # Process messages when queue reaches this size
BATCH_TIMEOUT = 10  # Seconds to wait before processing incomplete batch

WORKER_ID = str(uuid.uuid4())

# Separate queues for each topic
topic_queues = {
    MQTT_TOPIC_MIC: queue.Queue(),
    MQTT_TOPIC_ACC: queue.Queue(),
    MQTT_TOPIC_CAMERA: queue.Queue()
}

# Track last process time for each queue
last_process_time = {
    MQTT_TOPIC_MIC: time.time(),
    MQTT_TOPIC_ACC: time.time(),
    MQTT_TOPIC_CAMERA: time.time()
}

# PLEASE NOTE ALL THIS FUNCTION WILL BE RUNNING IN A PARALLEL PROCXESS 
# HENCE ITS BETTER TO JUST IMPORT INSIDE FUNCTIONS AND **NOT HAVE GLOBAL SCOPE** TO MAKE SURE THERE ARE NO LOCK ISSUES
def run_inference_and_publish(topic_queue):
    from mapping import topic_to_pipeline
    
    # Collect all messages in the queue up to threshold
    messages = []
    try:
        while len(messages) < BATCH_THRESHOLD and not topic_queue.empty():
            messages.append(topic_queue.get_nowait())
    except queue.Empty:
        pass
    
    if not messages:
        return None
        
    # All messages in a batch should have the same topic
    topic = messages[0]["topic"]
    pipeline = topic_to_pipeline[topic]    
    if pipeline:
        # Create a batch message with all data points
        batch_message = {
            "topic": topic,
            "batch_size": len(messages),
            "timestamp": time.time(),
            "data": messages
        }
        
        # Process the batch through the pipeline
        result = pipeline(batch_message)
        return result
    
    return None

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    message = json.loads(message)
    message["topic"] = msg.topic  # Add topic to message for processing
    if msg.topic == "inference/microphone":
        print(f"[{WORKER_ID}] Received job from Microphone Sensor")
        topic_queues[MQTT_TOPIC_MIC].put(message)
    
    elif msg.topic == "inference/accelerometer" :
        print(f"[{WORKER_ID}] Received job from Accelerometer Sensor")
        topic_queues[MQTT_TOPIC_ACC].put(message)
        
    elif msg.topic == "inference/camera":
        print(f"[{WORKER_ID}] Received job from Camera Sensor")
        topic_queues[MQTT_TOPIC_CAMERA].put(message)

def mqtt_subscribe():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.subscribe([(MQTT_TOPIC_MIC, 0), (MQTT_TOPIC_ACC, 0), (MQTT_TOPIC_CAMERA, 0)])
    client.loop_start()
    return client

def main():
    print(f"[{WORKER_ID}] Starting MQTT worker (distributed={IS_DISTRIBUTED})")
    
    # time.sleep(4)  # Allow time for DB tables to be created by server # hacky bug fix
    
    # Initialize the database
    print(f"[{WORKER_ID}] Initializing database...")
    init_db()
    
    if IS_DISTRIBUTED:
        worker = DistributedWorker()
        worker.start()
    else:
        client = mqtt_subscribe()
        with ProcessPoolExecutor(max_workers=8) as executor:
            while True:
                try:
                    for topic, q in topic_queues.items():
                        if not q.empty() and (q.qsize() >= BATCH_THRESHOLD or time.time() - last_process_time[topic] >= BATCH_TIMEOUT):
                            print(f"[{WORKER_ID}] Processing messages from topic: {topic}")
                            future = executor.submit(run_inference_and_publish, q)
                            last_process_time[topic] = time.time()
                except queue.Empty:
                    continue

if __name__ == "__main__":
    main()

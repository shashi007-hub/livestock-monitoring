import os
import time
import queue
import json
import uuid
from concurrent.futures import ProcessPoolExecutor
import paho.mqtt.client as mqtt
from mapping import topic_to_pipeline
from distributed_worker import DistributedWorker
from database.db import init_db

MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_MIC = os.getenv("MQTT_TOPIC_MIC", "inference/microphone")
MQTT_TOPIC_ACC= os.getenv("MQTT_TOPIC_ACC", "inference/accelerometer")
MQTT_TOPIC_CAMERA = os.getenv("MQTT_TOPIC_CAMERA", "inference/camera")
IS_DISTRIBUTED = os.getenv("IS_DISTRIBUTED", "false").lower() == "true"

WORKER_ID = str(uuid.uuid4())
message_queue = queue.Queue()

def run_inference_and_publish(message):
    pipline = topic_to_pipeline.get(message["job"])
    result = pipline(message["data"])
    return f"[{WORKER_ID}] Handled: {message}"

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    if msg.topic == "inference/microphone":
        print(f"[{WORKER_ID}] Received job from Microphone Sensor")
        message_queue.put(json.loads(message))
    
    elif msg.topic == "inference/accelerometer" :
        print(f"[{WORKER_ID}] Received job from Accelerometer Sensor")
        message_queue.put(json.loads(message))
        
    elif msg.topic == "inference/camera":
        print(f"[{WORKER_ID}] Received job from Camera Sensor")
        message_queue.put(json.loads(message))

def mqtt_subscribe():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.subscribe([(MQTT_TOPIC_MIC, 0), (MQTT_TOPIC_ACC, 0), (MQTT_TOPIC_CAMERA, 0)])
    client.loop_start()
    return client

def main():
    print(f"[{WORKER_ID}] Starting MQTT worker (distributed={IS_DISTRIBUTED})")
    
    time.sleep(2)  # Allow time for DB tables to be created by server # hacky bug fix
    
    # Initialize the database
    print(f"[{WORKER_ID}] Initializing database...")
    init_db()
    
    if IS_DISTRIBUTED:
        worker = DistributedWorker()
        worker.start()
    else:
        client = mqtt_subscribe()
        with ProcessPoolExecutor(max_workers=4) as executor:
            while True:
                try:
                    message = message_queue.get(timeout=1)
                    executor.submit(run_inference_and_publish, message)
                except queue.Empty:
                    continue

if __name__ == "__main__":
    main()

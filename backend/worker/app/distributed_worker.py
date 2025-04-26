import os
import json
import time
import uuid
import random
import paho.mqtt.client as mqtt

# Fix imports to use package paths
from app.mapping import topic_to_pipeline
import threading
import psutil
from concurrent.futures import ProcessPoolExecutor

MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_IN = os.getenv("MQTT_TOPIC_IN", "inference/topic")
MQTT_TOPIC_BIDS = "auction/bids"
NUM_NODES = int(os.getenv("NUM_NODES", 2))

class DistributedWorker:
    def __init__(self):
        self.worker_id = str(uuid.uuid4())
        self.bids = {}
        self.client = None
        self.executor = None

    def get_score(self):
        # Lower is better
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        return cpu + mem

    def run_inference_and_publish(self, message):
        time.sleep(1)  # Simulate inference
        pipeline = topic_to_pipeline.get(message["job"])
        result = pipeline(message["data"])

        return f"[{self.worker_id}] Handled: {message}"

    def on_message(self, client, userdata, msg):
        if msg.topic == MQTT_TOPIC_IN:
            print(f"[{self.worker_id}] Received job: {msg.payload.decode()}")
            message = json.loads(msg.payload.decode())
            score = self.get_score()
            bid_payload = json.dumps({
                "worker_id": self.worker_id,
                "score": score,
                "job_id": message["job_id"],
                "job": message["job"],
            })
            client.publish(MQTT_TOPIC_BIDS, bid_payload)

        elif msg.topic == MQTT_TOPIC_BIDS:
            try:
                bid = json.loads(msg.payload.decode())
                job = bid["job"]
                score = bid["score"]
                worker_id = bid["worker_id"]
                self.bids.setdefault(job, []).append((score, worker_id))
            except Exception as e:
                print(f"[{self.worker_id}] Error parsing bid: {e}")

    def bid_watcher(self):
        while True:
            for job, bid_list in list(self.bids.items()):
                if len(bid_list) >= NUM_NODES:
                    # Find the best bid (lowest score)
                    best_score, best_worker = min(bid_list)
                    if best_worker == self.worker_id:
                        print(f"[{self.worker_id}] Won bid for job: {job}")
                        self.executor.submit(self.run_inference_and_publish, job)
                    del self.bids[job]
            time.sleep(0.1)

    def mqtt_subscribe(self):
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        self.client.subscribe([(MQTT_TOPIC_IN, 0), (MQTT_TOPIC_BIDS, 0)])
        self.client.loop_start()
        return self.client

    def start(self):
        print(f"[{self.worker_id}] Starting distributed worker")
        self.client = self.mqtt_subscribe()
        
        with ProcessPoolExecutor(max_workers=4) as executor:
            self.executor = executor
            # Start background bid watcher
            threading.Thread(target=self.bid_watcher, daemon=True).start()
            
            # Keep the main thread alive
            while True:
                time.sleep(0.1)
import os
import json
import time
import uuid
import random
import paho.mqtt.client as mqtt
from app.mapping import microphone_pipeline,accelerometer_pipeline,camera_pipeline
topic_to_pipeline = {
    "inference/microphone": microphone_pipeline,
    "inference/accelerometer": accelerometer_pipeline,
    "inference/camera": camera_pipeline,
}
import threading
import psutil
from concurrent.futures import ProcessPoolExecutor
from threading import Lock
from queue import Queue
from collections import defaultdict

MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_IN = os.getenv("MQTT_TOPIC_IN", "inference/topic")
MQTT_TOPIC_BIDS = "auction/bids"
NUM_NODES = int(os.getenv("NUM_NODES", 2))

class DistributedWorker:
    def __init__(self):
        """
        Initializes in the main process.
        Creates thread-safe data structures for cross-thread communication.
        """
        self.worker_id = str(uuid.uuid4())
        self.bids_lock = Lock()
        self.bids = {}
        self.client = None
        self.executor = None
        self.job_queue = Queue()  # Thread-safe queue for jobs
        
    def get_score(self):
        """
        Runs in the MQTT client thread.
        Thread-safe as it only reads system metrics.
        """
        # Lower is better
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        return cpu + mem

    def run_inference_and_publish(self, messages):
        """
        Runs in a separate process from ProcessPoolExecutor.
        Each invocation creates a new process.
        
        Args:
            messages: List of messages to process in batch
        """
        try:
            if not isinstance(messages, list):
                messages = [messages]  # Handle single message case for backward compatibility
                
            if not messages:
                return None
                
            # All messages in a batch should have the same topic
            topic = messages[0]["topic"]
            bovine_id = messages[0]["bovine_id"]
            
            # Create batch message
            batch_message = {
                "topic": topic,
                "bovine_id": bovine_id,
                "batch_size": len(messages),
                "timestamp": time.time(),
                "data": messages
            }
            
            # Get and run appropriate pipeline
            pipeline = topic_to_pipeline.get(topic)
            if pipeline:
                result = pipeline(batch_message)
                print(f"[{self.worker_id}] Successfully processed batch of {len(messages)} messages for bovine {bovine_id}")
                return result
                
        except Exception as e:
            print(f"[{self.worker_id}] Error in inference: {str(e)}")
        return None

    def on_message(self, client, userdata, msg):
        """
        Callback function that runs in the MQTT client thread.
        Uses thread-safe data structures for cross-thread communication.
        """
        try:
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
                bid = json.loads(msg.payload.decode())
                job = bid["job"]
                score = bid["score"]
                worker_id = bid["worker_id"]
                
                # Thread-safe bid management
                with self.bids_lock:
                    if job not in self.bids:
                        self.bids[job] = []
                    self.bids[job].append((score, worker_id))
                    
        except Exception as e:
            print(f"[{self.worker_id}] Error in message handler: {str(e)}")

    def bid_watcher(self):
        """
        Runs in a dedicated thread created by start().
        Uses thread-safe operations to manage bids and job queue.
        """
        while True:
            jobs_to_process = []
            
            # Thread-safe bid processing
            with self.bids_lock:
                for job, bid_list in list(self.bids.items()):
                    if len(bid_list) >= NUM_NODES:
                        # Find the best bid (lowest score)
                        best_score, best_worker = min(bid_list)
                        if best_worker == self.worker_id:
                            jobs_to_process.append(job)
                        del self.bids[job]
            
            # Queue jobs for processing
            for job in jobs_to_process:
                print(f"[{self.worker_id}] Won bid for job: {job}")
                self.job_queue.put(job)
            
            # Process queued jobs
            while not self.job_queue.empty():
                job = self.job_queue.get()
                future = self.executor.submit(self.run_inference_and_publish, job)
                self.job_queue.task_done()
            
            time.sleep(0.1)

    def mqtt_subscribe(self):
        """
        Runs in the main thread but creates a background thread for MQTT operations.
        """
        client = mqtt.Client()
        client.on_message = self.on_message
        client.connect(MQTT_BROKER, MQTT_PORT)
        client.subscribe([(MQTT_TOPIC_IN, 0), (MQTT_TOPIC_BIDS, 0)])
        client.loop_start()  # Starts a background thread for MQTT
        return client

    def start(self):
        """
        Main entry point that runs in the main thread.
        Initializes components and creates worker threads/processes.
        """
        print(f"[{self.worker_id}] Starting distributed worker")
        self.client = self.mqtt_subscribe()
        
        with ProcessPoolExecutor(max_workers=4) as executor:
            self.executor = executor
            
            # Start background bid watcher thread
            bid_watcher_thread = threading.Thread(
                target=self.bid_watcher, 
                daemon=True,
                name="BidWatcher"
            )
            bid_watcher_thread.start()
            
            # Keep the main thread alive
            try:
                while True:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print(f"[{self.worker_id}] Shutting down...")
                self.client.loop_stop()
                self.client.disconnect()
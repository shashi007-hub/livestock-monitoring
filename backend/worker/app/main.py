import os
import time
import queue
import json
import uuid
import threading
import psutil
from concurrent.futures import ProcessPoolExecutor
import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_IN = os.getenv("MQTT_TOPIC_IN", "inference/topic")
MQTT_TOPIC_OUT = os.getenv("MQTT_TOPIC_OUT", "results/topic")
MQTT_TOPIC_BIDS = "auction/bids"
NUM_NODES = int(os.getenv("NUM_NODES", 2))

IS_DISTRIBUTED = os.getenv("IS_DISTRIBUTED", "false").lower() == "true"
# IS_DISTRIBUTED = True 

WORKER_ID = str(uuid.uuid4())  # Unique ID for this node
message_queue = queue.Queue()
bids = {}

# Inference function that also publishes results
def run_inference_and_publish(message):
    import paho.mqtt.client as mqtt
    time.sleep(1)  # Simulate inference
    result = f"Processed({message})"

    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.loop_start()
    client.publish(MQTT_TOPIC_OUT, result)
    client.loop_stop()
    client.disconnect()

    return f"[{WORKER_ID}] Handled: {message}"

def get_score():
    # Lower is better
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    return cpu + mem  # You can tune this formula

# MQTT callbacks
def on_message(client, userdata, msg):
    message = msg.payload.decode()

    if msg.topic == MQTT_TOPIC_IN:
        print(f"[{WORKER_ID}] Received job: {message}")
        message = json.loads(message)
        if IS_DISTRIBUTED:
            score = get_score()
            bid_payload = json.dumps({
                "worker_id": WORKER_ID,
                "score": score,
                "job_id:": message["job_id"],
                "job": message["job"],
            })
            client.publish(MQTT_TOPIC_BIDS, bid_payload)
        else:
            message_queue.put(message)

    elif msg.topic == MQTT_TOPIC_BIDS:
        try:
            bid = json.loads(msg.payload.decode())
            job = bid["job"]
            score = bid["score"]
            worker_id = bid["worker_id"]
            bids.setdefault(job, []).append((score, worker_id))
        except Exception as e:
            print(f"[{WORKER_ID}] Error parsing bid: {e}")

def mqtt_subscribe():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.subscribe([(MQTT_TOPIC_IN, 0), (MQTT_TOPIC_BIDS, 0)])
    client.loop_start()
    return client

def bid_watcher(executor):
    while True:
        for _ in range(3):
            print("bid_watcher: sleeping for 1 second")
            time.sleep(1)
         # Check for completed auctions every 2 seconds
        print("bid_watcher: checking for completed auctions")
        for job, bid_list in list(bids.items()):
            if len(bid_list) < NUM_NODES:
                continue

            # Sort bids by score
            bid_list.sort()
            winner_score, winner_id = bid_list[0]

            if winner_id == WORKER_ID:
                print(f"[{WORKER_ID}] Won the auction for job: {job} with score {winner_score}")
                executor.submit(run_inference_and_publish, job)
                
            else:
                print(f"[{WORKER_ID}] Lost auction for job: {job}")

            del bids[job]  # Cleanup

def main():
    print(f"[{WORKER_ID}] Starting MQTT worker (distributed={IS_DISTRIBUTED})")
    client = mqtt_subscribe()

    with ProcessPoolExecutor(max_workers=2) as executor:
        if IS_DISTRIBUTED:
            # Start background bid watcher
            threading.Thread(target=bid_watcher, args=(executor,), daemon=True).start()

        while True:
            if not IS_DISTRIBUTED:
                try:
                    message = message_queue.get(timeout=1)
                    executor.submit(run_inference_and_publish, message)
                except queue.Empty:
                    continue
            else:
                time.sleep(0.1)  # Let bid_watcher handle everything

if __name__ == "__main__":
    main()

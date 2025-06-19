import time
import json
import base64

import os
import wave
import paho.mqtt.client as  mqtt

# Configs
BOVINE_ID = "4"
MQTT_BROKER = "192.168.101.148"
MQTT_PORT = 1883
MQTT_TOPIC = b"inference/microphone"
WAV_FILE_PATH = "/Users/apple/Documents/pragathi-ai/git-repo/livestock-monitoring/test_scripts/bite1.wav"  # Must be mono, 16-bit, 22500Hz
idx = None
# Audio chunking config
CHUNK_SIZE = 1024

def publish_message(broker, port, topic, message):

    client = mqtt.Client()
    client.connect(broker, port, 60)
    json_message = message
    client.publish(topic, json_message)
    if idx is not None:
        print(f"Published index: {idx}")
    client.disconnect()

# client = mqtt_connect("esp32-client", MQTT_BROKER, MQTT_PORT)

def sim():
    broker = "localhost"
    port = 1883
    topics = "inference/microphone"
    try:
        with wave.open(WAV_FILE_PATH, 'rb') as wf:
            assert wf.getnchannels() == 1, "Audio file must be mono"
            assert wf.getsampwidth() == 2, "Audio file must be 16-bit"
            assert wf.getframerate() == 22500, "Audio must be 22500Hz"

            total_bytes = wf.getnframes() * wf.getsampwidth()
            num_chunks = total_bytes // CHUNK_SIZE + (1 if total_bytes % CHUNK_SIZE else 0)

            print(f"Audio will be split into {num_chunks} chunks")

            # Send start chunk
            start_msg = json.dumps({
                "bovine_id": BOVINE_ID,
                "type": "start",
                "timestamp": time.time(),
                "chunks": num_chunks
            })
            print("start_msg:", start_msg)
            publish_message(broker, port, topics, start_msg)
            # client.publish(MQTT_TOPIC, start_msg)

            # Read and send chunks
            chunk_index = 0
            while True:
                buf = wf.readframes(CHUNK_SIZE // wf.getsampwidth())  # samples not bytes
                if not buf:
                    break

                encoded = base64.b64encode(buf).decode().strip()


                data_msg = json.dumps({
                    "bovine_id": BOVINE_ID,
                    "type": "data",
                    "index": chunk_index,
                    "data": encoded
                })
                print("data_msg:", data_msg)
                publish_message(broker, port, topics, data_msg)
                # client.publish(MQTT_TOPIC, data_msg)

                chunk_index += 1

            # Send end chunk
            end_msg = json.dumps({
                "bovine_id": BOVINE_ID,
                "type": "end",
                "timestamp": time.time()
            })
            print("end_msg:", end_msg)
            publish_message(broker, port, topics, end_msg)
            # client.publish(MQTT_TOPIC, end_msg)

            print("✅ Finished sending audio file")

    finally:
        # client.disconnect()
        pass


if __name__ == "__main__":
    sim()
import datetime
import json
import paho.mqtt.client as mqtt
import time
import random

def read_json_audio(file_path):
    """Read a JSON file and return its audio data."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    # Adjust the key if your JSON structure is different
    return data

def publish_message(broker, port, topic, message):
    client = mqtt.Client()
    client.connect(broker, port, 60)
    json_message = json.dumps(message)
    client.publish(topic, json_message)
    if idx is not None:
        print(f"Published index: {idx}")
    client.disconnect()

if __name__ == "__main__":
    broker = "localhost"
    port = 1883
    topics = "inference/microphone"
    json_file_path = "/Users/apple/Documents/pragathi-ai/git-repo/livestock-monitoring/test_scripts/sample_chunks.json" # Path to your JSON file

    audio_raw = read_json_audio(json_file_path)
    for idx, sample in enumerate(audio_raw):
        message = sample
        publish_message(broker, port, topics, message)
        time.sleep(0.01)
        if (idx + 1) % 50 == 0:
            time.sleep(2)
        
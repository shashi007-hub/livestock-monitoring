# pip install paho-mqtt


import datetime
import json
import paho.mqtt.client as mqtt
import time
import random
import wave

def read_wav_as_raw(file_path):
    """Read a .wav file and return its raw audio data."""
    with wave.open(file_path, 'rb') as wav_file:
        raw_data = wav_file.readframes(wav_file.getnframes())
    return raw_data

def publish_message(broker, port, topic, message):
    # Create an MQTT client instance
    client = mqtt.Client()

    # Connect to the MQTT broker
    client.connect(broker, port, 60)

    # Convert the message to JSON
    json_message = json.dumps(message)

    # Publish the JSON message to the specified topic
    client.publish(topic, json_message)
    print(f"Published to {topic}: {json_message}")

    # Disconnect after sending
    client.disconnect()

if __name__ == "__main__":
    # Example usage
    broker = "localhost"  # Replace with your broker
    port = 1883  # Replace with your MQTT port
    topics = ["inference/microphone"]  # Replace with your desired topic
    import random
    wav_file_path = "test_scripts/recording_01_bite_0.wav"  # Replace with the path to your .wav file

    raw_audio_data = read_wav_as_raw(wav_file_path)
    message = {
        "bovine_id": "3",
        "audio_raw":list(raw_audio_data),
        "probability": 0.9,
        "timestamp": datetime.datetime.now().isoformat(),
    }
    for i in range(3):
        publish_message(broker, port, random.choice(topics), message)
        time.sleep(1)

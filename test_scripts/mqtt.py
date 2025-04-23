# pip install paho-mqtt


import datetime
import json
import paho.mqtt.client as mqtt

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
    message = {
        "bovine_id": "2",
        "probability": 0.9,
        "timestamp": datetime.datetime.now().isoformat(),
    }
    publish_message(broker, port, random.choice(topics), message)

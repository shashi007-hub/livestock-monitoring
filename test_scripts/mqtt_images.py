# pip install paho-mqtt


import datetime
import json
import paho.mqtt.client as mqtt
import time
import random
import wave
import base64
import cv2

def encode_image_to_base64(image_path):
    """Encodes an image file to a base64 string.

    Args:
        image_path: The path to the image file.

    Returns:
        A base64 string representing the image.
    """
    try:
        # Read the image using OpenCV
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        
        # Encode the image data to base64
        encoded_string = base64.b64encode(image_data).decode('utf-8')

        # Return the base64 string with data URL prefix
        return f"data:image/jpeg;base64,{encoded_string}" 
    except Exception as e:
        print(f"Error encoding image to base64: {e}")
        return None

# Example usage

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
    topics = ["inference/camera"]  # Replace with your desired topic
    import random
     # Replace with the path to your .wav file
    image_path = r"/Users/apple/Documents/pragathi-ai/git-repo/livestock-monitoring/test_scripts/cows with lumpy skin disease_1.png" 
     # Replace with your image path
    base64_string = encode_image_to_base64(image_path)
    message = None
    if base64_string:
        message = {
            "bovine_id": "3",
            "image_raw": base64_string,  # Replace with actual image data
            "timestamp": datetime.datetime.now().isoformat(),
        }
    else:
        print("Failed to encode image. Exiting.")   
    for i in range(1):
        publish_message(broker, port, random.choice(topics), message)
        time.sleep(1)

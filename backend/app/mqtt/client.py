import paho.mqtt.client as mqtt
from core.config import settings

mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker:", rc)
    client.subscribe("inference/results")

def on_message(client, userdata, msg):
    print(f"Received from {msg.topic}: {msg.payload.decode()}")

def start_mqtt():
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT)
    mqtt_client.loop_start()

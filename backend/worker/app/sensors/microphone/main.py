# main.py
import time
import json
import ubinascii
import machine
from machine import Pin, I2S
from umqtt.simple import MQTTClient

# Fixed metadata
BOVINE_ID = "cow-001"
MQTT_BROKER = "192.168.101.148"
MQTT_PORT = 1883
MQTT_TOPIC = b"inference/microphone"

# I2S Microphone config (INMP441)
i2s = I2S(
    0,
    sck=Pin(18),
    ws=Pin(19),
    sd=Pin(22),
    mode=I2S.RX,
    bits=16,
    format=I2S.MONO,
    rate=22500,
    ibuf=8192
)

# Audio config
CHUNK_SIZE = 1024
SAMPLE_RATE = 22500
BITS_PER_SAMPLE = 16
CHANNELS = 1
DURATION_SEC = 5
TOTAL_BYTES = SAMPLE_RATE * (BITS_PER_SAMPLE // 8) * CHANNELS * DURATION_SEC
NUM_CHUNKS = TOTAL_BYTES // CHUNK_SIZE + (1 if TOTAL_BYTES % CHUNK_SIZE else 0)

print(f"Audio will be split into {NUM_CHUNKS} chunks")

def mqtt_connect(client_id, server, port=1883, max_retries=10):
    attempt = 0
    while attempt < max_retries:
        try:
            client = MQTTClient(client_id, server, port)
            client.connect()
            print("✅ Connected to MQTT broker")
            return client
        except Exception as e:
            print(f"❌ MQTT connect failed: {e}")
            delay = 1 << attempt
            print(f"⏳ Retrying in {delay}s...")
            time.sleep(delay)
            attempt += 1
    raise RuntimeError("Failed to connect to MQTT broker")

client = mqtt_connect("esp32-client", MQTT_BROKER, MQTT_PORT)

def main():
    try:
        buf = bytearray(CHUNK_SIZE)

        while True:
            print("Recording 5s of audio and sending...")
            audio_data = []

            # Send start chunk
            start_msg = json.dumps({
                "bovine_id": BOVINE_ID,
                "type": "start",
                "timestamp": time.time(),
                "chunks": NUM_CHUNKS
            })
            client.publish(MQTT_TOPIC, start_msg)

            # Read and send chunks
            chunk_index = 0
            bytes_left = TOTAL_BYTES

            while bytes_left > 0:
                read_len = min(CHUNK_SIZE, bytes_left)
                buf = bytearray(read_len)
                i2s.readinto(buf)
                encoded = ubinascii.b2a_base64(buf).decode().strip()

                data_msg = json.dumps({
                    "bovine_id": BOVINE_ID,
                    "type": "data",
                    "index": chunk_index,
                    "data": encoded
                })
                client.publish(MQTT_TOPIC, data_msg)

                chunk_index += 1
                bytes_left -= read_len

            # Send end chunk
            end_msg = json.dumps({
                "bovine_id": BOVINE_ID,
                "type": "end",
                "timestamp": time.time()
            })
            client.publish(MQTT_TOPIC, end_msg)

            print("Finished sending one 5s audio session")
            time.sleep(1)

    finally:
        i2s.deinit()
        client.disconnect()


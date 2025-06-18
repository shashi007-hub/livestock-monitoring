import json
import base64
import paho.mqtt.client as mqtt

BOVINE_ID_FILTER = "cow-001"
AUDIO_TOPIC = "inference/microphone"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker")
        client.subscribe(AUDIO_TOPIC)
    else:
        print("❌ Failed to connect, return code %d\n", rc)

chunks = {}
        

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        bovine_id = payload.get("bovine_id")
        msg_type = payload.get("type")

        if bovine_id != BOVINE_ID_FILTER:
            return  # Skip other cows

        
        if msg_type == "start":
            print(f"🐄 {bovine_id} started sending audio")
            chunks[bovine_id] = {
                "total": payload.get("chunks"),
                "data": {}
            }

        elif msg_type == "data":
            index = payload.get("index")
            data = base64.b64decode(payload["data"])
            if bovine_id in chunks:
                chunks[bovine_id]["data"][index] = data
            print(f"📦 Received chunk {index}")

        elif msg_type == "end":
            print(f"✅ Finished receiving from {bovine_id}")
            save_audio(bovine_id)
        

    except Exception as e:
        print(f"⚠️ Error: {e}")

import wave

def save_audio(bovine_id):
    if bovine_id not in chunks:
        print(f"⚠️ No chunks found for {bovine_id}")
        return

    data_dict = chunks[bovine_id]["data"]
    ordered_data = [data_dict[i] for i in sorted(data_dict)]
    audio_bytes = b''.join(ordered_data)

    raw_filename = f"{bovine_id}_audio.raw"
    wav_filename = f"{bovine_id}_audio.wav"

    # Save raw audio for reference (optional)
    with open(raw_filename, "wb") as f:
        f.write(audio_bytes)

    # WAV file settings — must match ESP32 recording config
    sample_rate = 22500
    sample_width = 2  # bytes (16 bits)
    channels = 1

    with wave.open(wav_filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_bytes)

    print(f"💾 Saved audio to {wav_filename}")
    del chunks[bovine_id]

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_forever()

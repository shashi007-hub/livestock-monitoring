import pandas as pd
import json
import paho.mqtt.client as mqtt
import time
from datetime import datetime

def preprocess_csv(file_path):
    """Preprocess the CSV file to split stacked columns and values into proper rows."""
    # Read as a single column (no split)
    df_raw = pd.read_csv(file_path, header=None)

        # Split the first column into multiple columns
    split_df = df_raw[0].str.split(expand=True)

        # Convert all to numeric immediately (coerce any bad values to NaN)
    split_df = split_df.apply(pd.to_numeric, errors='coerce')
    # Drop rows with NaN values
    split_df = split_df.dropna()
    # Reset index
    split_df = split_df.reset_index(drop=True)
        # Rename columns if number matches
    split_df.columns = [
            'Time(s)', 'Acceleration_x', 'Acceleration_y', 'Acceleration_z',
            'Gravity_x', 'Gravity_y', 'Gravity_z',
            'Rotation_x', 'Rotation_y', 'Rotation_z',
            'Roll', 'Pitch', 'Yaw'
        ][:split_df.shape[1]]
    split_df = split_df.drop(columns=['Time(s)'])
    # Convert to a list of dictionaries
    return split_df.to_dict(orient="records")

def create_json_records(data, bovine_id):
    """Create an array of JSON objects with the required structure."""
    json_records = []
    for row in data:
        accelerometer_data = {key: value for key, value in row.items()}
        json_record = {
            "bovine_id": bovine_id,
            "acclerometer_data": accelerometer_data,
            "timestamp": datetime.now().isoformat()  # Current timestamp in ISO format
        }
        json_records.append(json_record)
    return json_records

def publish_message(broker, port, topic, message):
    """Publish a JSON message to an MQTT topic."""
    client = mqtt.Client()
    client.connect(broker, port, 60)
    json_message = json.dumps(message)
    client.publish(topic, json_message)
    print(f"Published to {topic}: {json_message}")
    client.disconnect()

if __name__ == "__main__":
    # Configuration
    broker = "164.52.194.74"  # Replace with your broker
    port = 1883  # Replace with your MQTT port
    topic = "inference/accelerometer"  # Replace with your desired topic
    csv_file_path = "test_scripts/Illnessdegree_5_Leg_frontright_Acquisitiondata_17_05_2022_Acquisitiontime_08_29_02.csv"  # Replace with your CSV file path
    bovine_id = "3"  # Replace with your bovine ID

    # Preprocess the CSV file
    data = preprocess_csv(csv_file_path)

    # Create JSON records
    json_records = create_json_records(data, bovine_id)
    count = 0
    print(f"Total records to publish: {len(json_records)}")
    # Publish each JSON record
    for record in json_records:
        
        count += 1
        publish_message(broker, port, topic, record)
        if count % 500 == 0:
            time.sleep(1)
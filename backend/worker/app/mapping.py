from datetime import datetime
from database.db import db_session
from database.models import DistressCall

def microphone_pipeline(data):
    # Process microphone data and create a distress call record
    print("Processing microphone data:", data)
    
    # Ideally have model get the data but I hope you get my point here 
    
    # Extract data from the message
    bovine_id = data.get('bovine_id')
    probability = data.get('probability', 0.0)
    
    if bovine_id is not None:
        # Create new distress call record
        distress_call = DistressCall(
            bovine_id=bovine_id,
            timestamp=datetime.utcnow(),
            probability=probability
        )
        
        # Add to database
        db = db_session()
        try:
            db.add(distress_call)
            db.commit()
            print(f"Added distress call for bovine {bovine_id}")
        except Exception as e:
            db.rollback()
            print(f"Error adding distress call: {e}")
        finally:
            db.close()

def accelerometer_pipeline(data):
    # Process accelerometer data
    print("Processing accelerometer data:", data)
    
def camera_pipeline(data):
    # Process camera data
    print("Processing camera data:", data)

topic_to_pipeline = {
    "inference/microphone": microphone_pipeline,
    "inference/accelerometer": accelerometer_pipeline,
    "inference/camera": camera_pipeline,
}
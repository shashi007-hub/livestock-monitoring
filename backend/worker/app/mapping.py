# PLEASE NOTE ALL THESE FUNCTIONS WILL BE RUNNING IN A PARALLEL PROCXESS 
# HENCE ITS BETTER TO JUST IMPORT INSIDE FUNCTIONS AND **NOT HAVE GLOBAL SCOPE** TO MAKE SURE THERE ARE NO LOCK ISSUES


def validate_batch(batch_data):
    """Validate that all messages in batch are from same bovine and have required fields"""
    if not batch_data.get('data'):
        return False, "Empty batch"
        
    bovine_id = batch_data['data'][0]['bovine_id']
    for msg in batch_data['data']:
        if msg['bovine_id'] != bovine_id:
            return False, f"Mismatched bovine_ids in batch: {msg['bovine_id']} != {bovine_id}"
    return True, None

def microphone_pipeline(batch_data):
    from datetime import datetime
    from app.database.db import db_session
    from app.database.models import DistressCall
    from app.alerts import send_sms_alert

    
    print(f"Processing microphone batch data: {len(batch_data['data'])} messages for bovine {batch_data['data'][0]['bovine_id']}",flush=True)
    
    # Validate batch
    # This might not be a thing to do actually but i'll have to check
    # is_valid, error = validate_batch(batch_data)
    # if not is_valid:
    #     print(f"Invalid batch: {error}")
    #     return {"status": "error", "message": error}
    
    db = db_session()
    try:
        # Calculate average probability across all messages
        probabilities = []
        for message in batch_data['data']:
            prob = message.get("probability", 0)
            if prob > 0.5:  # Only consider significant probabilities
                probabilities.append(prob)
        
        if not probabilities:
            print("No significant probabilities found in batch (>0.5)")
            return {"status": "success", "avg_probability": 0}
            
        avg_probability = sum(probabilities) / len(probabilities)
        
        # Create aggregated distress call record
        distress_call = DistressCall(
            bovine_id=batch_data['data'][0]['bovine_id'],
            timestamp=datetime.utcnow(),
            probability=avg_probability
        )
        
        print(avg_probability)
        
        db.add(distress_call)
        db.commit()
        print(f"Added aggregated distress call with probability {avg_probability:.3f}",flush=True)
        
        # Post-inference action if probability is very high
        if avg_probability > 0.8:
            print(f"High distress detected! Triggering alert for bovine {batch_data['data'][0]['bovine_id']}",flush=True)
            send_sms_alert(f"High distress detected for bovine {batch_data['data'][0]['bovine_id']} with probability {avg_probability:.2f}",batch_data['data'][0]['bovine_id'])
        
        return {"status": "success", "avg_probability": avg_probability}
        
    except Exception as e:
        db.rollback()
        print(f"Error processing microphone batch: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

def accelerometer_pipeline(batch_data):
    pass

def camera_pipeline(batch_data):
    pass


# PLEASE NOTE ALL THESE FUNCTIONS WILL BE RUNNING IN A PARALLEL PROCXESS 
# HENCE ITS BETTER TO JUST IMPORT INSIDE FUNCTIONS AND **NOT HAVE GLOBAL SCOPE** TO MAKE SURE THERE ARE NO LOCK ISSUES
def microphone_pipeline(batch_data):
    from datetime import datetime
    from database.db import db_session
    from database.models import DistressCall
    
    print("Processing microphone batch data:", batch_data)
    db = db_session()
    
    try:
        # Calculate average probability across all messages
        probabilities = []
        for message in batch_data['data']:
            prob = message.get('probability', 0)
            if prob > 0.5:  # Only consider significant probabilities
                probabilities.append(prob)
        
        if not probabilities:
            return None
            
        avg_probability = sum(probabilities) / len(probabilities)
        
        # Create aggregated distress call record
        distress_call = DistressCall(
            bovine_id=batch_data['data'][0]['bovine_id'],  # Use first message's bovine_id
            timestamp=datetime.utcnow(),
            probability=avg_probability
        )
        
        db.add(distress_call)
        db.commit()
        print(f"Added aggregated distress call with probability {avg_probability}")
        
        # Post-inference action if probability is very high
        if avg_probability > 0.8:
            print(f"High distress detected! Triggering alert for bovine {batch_data['data'][0]['bovine_id']}")
            # Add alert logic here
        
        return {"status": "success", "avg_probability": avg_probability}
        
    except Exception as e:
        db.rollback()
        print(f"Error processing microphone batch: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

def accelerometer_pipeline(batch_data):
    from datetime import datetime
    from database.db import db_session
    from database.models import LamenessInference
    
    print("Processing accelerometer batch data:", batch_data)
    db = db_session()
    
    try:
        # Calculate average metric across all messages
        metrics = [msg.get('metric', 0) for msg in batch_data['data']]
        avg_metric = sum(metrics) / len(metrics)
        
        # Create aggregated lameness inference record
        lameness = LamenessInference(
            bovine_id=batch_data['data'][0]['bovine_id'],
            metric=avg_metric,
            timestamp=datetime.utcnow()
        )
        
        db.add(lameness)
        db.commit()
        print(f"Added aggregated lameness inference with metric {avg_metric}")
        
        # Post-inference action for high lameness scores
        if avg_metric > 0.7:
            print(f"High lameness detected! Triggering alert for bovine {batch_data['data'][0]['bovine_id']}")
            # Add alert logic here
            
        return {"status": "success", "avg_metric": avg_metric}
        
    except Exception as e:
        db.rollback()
        print(f"Error processing accelerometer batch: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

def camera_pipeline(batch_data):
    from datetime import datetime
    from database.db import db_session
    from database.models import OestrousCall
    
    print("Processing camera batch data:", batch_data)
    db = db_session()
    
    try:
        # Calculate average probability across all messages
        probabilities = [msg.get('probability', 0) for msg in batch_data['data']]
        avg_probability = sum(probabilities) / len(probabilities)
        
        # Create aggregated oestrous call record
        oestrous = OestrousCall(
            bovine_id=batch_data['data'][0]['bovine_id'],
            probability=avg_probability,
            timestamp=datetime.utcnow()
        )
        
        db.add(oestrous)
        db.commit()
        print(f"Added aggregated oestrous call with probability {avg_probability}")
        
        # Post-inference action for high probability
        if avg_probability > 0.85:
            print(f"High oestrous probability! Triggering alert for bovine {batch_data['data'][0]['bovine_id']}")
            # Add alert logic here
            
        return {"status": "success", "avg_probability": avg_probability}
        
    except Exception as e:
        db.rollback()
        print(f"Error processing camera batch: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

topic_to_pipeline = {
    "inference/microphone": microphone_pipeline,
    "inference/accelerometer": accelerometer_pipeline,
    "inference/camera": camera_pipeline,
}
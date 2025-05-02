import os
from twilio.rest import Client

from db.models import Bovine, User


# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_FROM_NUMBER = os.getenv('TWILIO_FROM_NUMBER')
ALERT_TO_NUMBER = os.getenv('ALERT_TO_NUMBER')

def _get_user_number_from_db(bovine_id):
    """
    Retrieve the user's phone number from the database based on bovine ID.
    
    Args:
        bovine_id (int): The ID of the bovine
    
    Returns:
        str: The user's phone number
    """
    from app.db.database import SessionLocal
    try:
        db = SessionLocal()
        bovine = db.query(Bovine).filter(Bovine.id == bovine_id).first()
        user = db.query(User).filter(User.id == bovine.owner_id).first()
        if user and user.phone_number:
            return user.phone_number
        else:
            print(f"No user found for bovine ID {bovine_id}")
            return None
    except Exception as e:
        print(f"Error retrieving user number from DB: {e}")
        return None
    finally:
        db.close()

def send_sms_alert(message,bovine_id):
    """
    Send an SMS alert using Twilio
    
    Args:
        message (str): The alert message to send
    
    Returns:
        dict: Status of the SMS sending operation
    """
    try:
        user_number = _get_user_number_from_db(bovine_id)
    except Exception as e:
        print(f"Error retrieving user number: {e} using the number from environemnt variable")
        user_number = os.getenv('ALERT_TO_NUMBER', user_number)
    
    
    
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, ALERT_TO_NUMBER]):
        print("Error: Twilio configuration missing. SMS alert not sent.")
        return {"status": "error", "message": "Twilio configuration missing"}
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        sms = client.messages.create(
            body=message,
            from_=TWILIO_FROM_NUMBER,
            to=ALERT_TO_NUMBER
        )
        print(f"SMS alert sent successfully. SID: {sms.sid}")
        return {"status": "success", "message_sid": sms.sid}
    except Exception as e:
        print(f"Error sending SMS alert: {e}")
        return {"status": "error", "message": str(e)}



        
        

# PLEASE NOTE ALL THESE FUNCTIONS WILL BE RUNNING IN A PARALLEL PROCXESS 
# HENCE ITS BETTER TO JUST IMPORT INSIDE FUNCTIONS AND **NOT HAVE GLOBAL SCOPE** TO MAKE SURE THERE ARE NO LOCK ISSUES

from enum import Enum
from keras.models import load_model 
from PIL import Image
import librosa
import numpy as np
import os
import wave
import onnxruntime as ort
from datetime import datetime, timedelta
from app.database.db import db_session
from app.database.models import DistressCall, FeedingPatterns, FeedingAnalytics, SMSAlerts,LamenessInference,SkinDiseases
from app.alerts import send_sms_alert

class Predictions(Enum):
    HFC = "HFC"
    LFC = "LFC"

def scale_melspec(mel_spec):
    target_size = (90, 200)
    norm_spec = librosa.util.normalize(mel_spec)
    norm_spec = (norm_spec * 255).astype(np.uint8)
    img = Image.fromarray(norm_spec)
    img = img.resize(target_size, Image.Resampling.LANCZOS)
    img_array = np.array(img)
    return img_array

    
def predict_from_wav(Model,WAV):
    y, sr = librosa.load(WAV)
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=2048, hop_length=512, n_mels=90)
    log_mel_spec = librosa.power_to_db(mel_spec)
    scaled_mel_spec = scale_melspec(log_mel_spec)

        # Shape it to model input: (1, H, W, 3)
    input_tensor = np.repeat(scaled_mel_spec[..., np.newaxis], 3, axis=-1)
    input_tensor = np.expand_dims(input_tensor, axis=0)

    print("Input tensor generated")

    print("Input shape:", input_tensor.shape)
    print("Model input shape:", Model.input_shape)

    prediction = Model.predict(input_tensor, verbose=1)

    print("Prediction made")

    pred_class = np.argmax(prediction)
    confidence = float(np.max(prediction))

    if pred_class == 1:
        return Predictions.HFC, confidence
    elif pred_class == 0:
        return Predictions.LFC, confidence


def validate_batch(batch_data):
    """Validate that all messages in batch are from same bovine and have required fields"""
    if not batch_data.get('data'):
        return False, "Empty batch"
        
    bovine_id = batch_data['data'][0]['bovine_id']
    for msg in batch_data['data']:
        if msg['bovine_id'] != bovine_id:
            return False, f"Mismatched bovine_ids in batch: {msg['bovine_id']} != {bovine_id}"
    return True, None

    # Helper functions
def save_raw_to_wav(raw_data, output_wav_path, sample_rate=22050):
    with wave.open(output_wav_path, 'wb') as wf:
        wf.setnchannels(1)        # Mono
        wf.setsampwidth(2)         # 16 bits = 2 bytes
        wf.setframerate(sample_rate)
        if isinstance(raw_data, list):
            raw_data = bytes(raw_data)
        wf.writeframes(raw_data)


def extract_mfcc(y, sr, n_mfcc=13, hop_length=256, n_fft=1024):
    mfcc_feat = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc,
                                    hop_length=hop_length, n_fft=n_fft)
    return mfcc_feat.astype(np.float32)

def process_audio(filepath, sr=22050):
    y, _ = librosa.load(filepath, sr=sr)
    mfcc = extract_mfcc(y, sr)
    if mfcc.shape[1] < 128:
        pad_width = 128 - mfcc.shape[1]
        mfcc = np.pad(mfcc, ((0, 0), (0, pad_width)), mode='constant')
    else:
        mfcc = mfcc[:, :128]
    feature = mfcc.flatten()
    feature = feature.astype(np.float32)
    feature = np.expand_dims(feature, axis=0)
    return feature

def run_inference(onnx_model_path, audio_path):
    session = ort.InferenceSession(onnx_model_path, providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    input_feature = process_audio(audio_path)
    outputs = session.run(None, {input_name: input_feature})
    predicted_class = outputs[0][0]
    return predicted_class

def microphone_pipeline(batch_data):
    """
    Process a batch of audio data from the microphone, run inference using ONNX model,
    and save results to the database.
    """

    onnx_model_path = "app/models/xgb_model.onnx"
    # Constants
    LABELS = {0: "chew", 1: "bite", 2: "chew-bite"}

    # Main pipeline
    print(f"Processing microphone batch data: {len(batch_data['data'])} messages for bovine {batch_data['data'][0]['bovine_id']}", flush=True)
    db = db_session()

    try:
        predictions = []
        # print("*****", batch_data['data'])
        for message in batch_data['data']:
            bovine_id = message['bovine_id']
            timestamp = datetime.strptime(message['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")  # Assume ISO format

            # Save raw audio to wav
            temp_wav_path = f"/tmp/{bovine_id}_{timestamp.timestamp()}.wav"
            print("Saving raw audio to wav:", temp_wav_path, flush=True)
            save_raw_to_wav(message['audio_raw'], temp_wav_path)
            print("Saved raw audio to wav:", temp_wav_path, flush=True)

            # Inference
            print("Running inference on wav file:", temp_wav_path, flush=True)
            pred = run_inference(onnx_model_path, temp_wav_path)
            print("Inference result:", pred, flush=True)

            label_idx = int(np.argmax(pred))
            label = LABELS[label_idx]

            predictions.append((timestamp, label))
            print(f"Predicted label for Bovine {bovine_id} at {timestamp}: {label}", flush=True)

            # Inference with Keras model (HFC / LFC)
            distress_model = load_model("app/models/cow_model.h5", compile=True)
            frequency_class, probability = predict_from_wav(distress_model,temp_wav_path)

            if frequency_class == Predictions.HFC: # or frequency_class == Predictions.LFC:
                distress_call = DistressCall(
                    bovine_id=bovine_id,
                    timestamp=timestamp,
                    probability=probability  # You can decide what value to store
                )
                send_sms_alert(f"ALERT! DISTRESS CALL from Bovine {bovine_id}!", bovine_id)
            
                db.add(distress_call)

                sms_alert = SMSAlerts(
                    user_id=1,
                    bovine_id=bovine_id,
                    timestamp=timestamp,
                    message=f"ALERT! DISTRESS CALL from Bovine {bovine_id}!"
                )

                db.add(sms_alert)

            # Cleanup
            os.remove(temp_wav_path)
            print("Removed temporary wav file:", temp_wav_path, flush=True)

            feeding_pattern = FeedingPatterns(
                bovine_id=bovine_id,
                timestamp=timestamp,
                bite_chew=label_idx
            )
            db.add(feeding_pattern)

        db.commit()

        return {"status": "success", "predictions": predictions}

    except Exception as e:
        db.rollback()
        print(f"Error processing microphone batch: {e.with_traceback()}", flush=True)
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

def accelerometer_pipeline(batch_data):
    from app.process_lamness.preprocess_lamness import predict_lameness
    from app.alerts import _get_bovin_name_from_db

    print("Accelerometer pipeline triggered ✅", flush=True)
    
    try:
        # Combine all acclerometer_data into a single list of dictionaries
        combined_data = {"acclerometer_data": []}
  
        for message in batch_data['data']:
            if 'acclerometer_data' in message:
                combined_data["acclerometer_data"].append(message['acclerometer_data'])  # append dict
            else:
                print(f"Missing 'acclerometer_data' in message: {message}", flush=True)

        print(f"Combined acclerometer_data data: {combined_data}", flush=True)

        # Extract Bovine ID and a dummy timestamp (replace with real logic if needed)
        bovine_id = batch_data['data'][0].get('bovine_id', 'unknown')
        timestamp = datetime.now().isoformat()
        print(f"Processing acclerometer_data message for Bovine {bovine_id} at {timestamp}", flush=True)
        
        # Predict lameness
        try:
            print("Calling predict_lameness with data:", combined_data, flush=True)
            results = predict_lameness(combined_data)
            if results >= 3:
                lameness_inference = LamenessInference(
                    bovine_id=bovine_id,
                    metric=results,
                    timestamp=timestamp
                )
                db_session.add(lameness_inference)
                db_session.commit()
                bovine_name = _get_bovin_name_from_db(bovine_id)
                message = "Alert: Your animal, {}, is showing signs of lameness. Please check on them as soon as possible.".format(bovine_name)
                send_sms_alert(message, bovine_id)

                sms_alert = SMSAlerts(
                user_id=1,
                bovine_id=bovine_id,
                timestamp=timestamp,
                message=message
            )
                print(sms_alert, flush=True)
                db_session.add(sms_alert)
                db_session.commit()
            else:   
                print(f"Lameness prediction for Bovine {bovine_id} is below threshold: {results}", flush=True)
            print(f"Predicted lameness for Bovine {bovine_id} at {timestamp}: {results}", flush=True)
        except Exception as e:
            print(f"Error in predict_lameness: {e}", flush=True)

    except Exception as e:
        print(f"Error in accelerometer_pipeline: {e}", flush=True)

    return "Accelerometer pipeline complete ✅"


 


def camera_pipeline(batch_data):
    from app.process_images.crop_detect import detect_cows, batch_detect_diseases
    from app.alerts import _get_bovin_name_from_db
    from app.database.models import SkinDiseases, SMSAlerts
    from app.alerts import send_sms_alert
    from datetime import datetime

    print("Camera pipeline triggered ✅", flush=True)

    try:
        for messages in batch_data['data']:
            try:
                # Process each message in the batch
                bovine_id = messages.get('bovine_id')
                if not bovine_id:
                    print("Missing bovine_id in message", flush=True)
                    continue

                print("Bovine ID:", bovine_id, flush=True)

                timestamp = datetime.strptime(messages['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
                print(f"Processing camera message at {timestamp}", flush=True)

                # Detect cows in the image
                detected_cows = detect_cows(messages['image_raw'])
                if not detected_cows:
                    print(f"No cows detected for Bovine {bovine_id} at {timestamp}", flush=True)
                    continue

                # Detect diseases in the detected cows
                diseases = batch_detect_diseases(detected_cows)
                if not diseases:
                    print(f"No diseases detected for Bovine {bovine_id} at {timestamp}", flush=True)
                    continue

                print("Diseases detected:", diseases, flush=True)

                # Extract disease details
                bovine_tag = diseases[0]['Bovine_tag']
                disease = diseases[0]['disease_status'][0]
                bovine_id = bovine_tag
                # Save disease inference to the database
                disease_inference = SkinDiseases(
                    bovine_id=bovine_tag,
                    timestamp=timestamp,
                    disease=disease
                )
                db_session.add(disease_inference)
                db_session.commit()
                print(f"Disease inference saved for Bovine {bovine_tag}", flush=True)

                # Send SMS alert
                bovine_name = _get_bovin_name_from_db(bovine_tag)
                message = f"Alert: Your animal, {bovine_name}, is showing signs of disease: {disease} skin disease. Please check on them as soon as possible."
                send_sms_alert(message, bovine_tag)

                # Save SMS alert to the database
                sms_alert = SMSAlerts(
                    user_id=1,
                    bovine_id=bovine_id,
                    timestamp=timestamp,
                    message=message
                )
                db_session.add(sms_alert)
                db_session.commit()
                print(f"SMS alert saved for Bovine {bovine_id}", flush=True)

            except Exception as e:
                db_session.rollback()
                print(f"Error processing message for Bovine {bovine_id}: {e}", flush=True)

    except Exception as e:
        print(f"Error in camera pipeline: {e}", flush=True)

    return "Camera pipeline triggered ✅"

# PLEASE NOTE ALL THESE FUNCTIONS WILL BE RUNNING IN A PARALLEL PROCXESS 
# HENCE ITS BETTER TO JUST IMPORT INSIDE FUNCTIONS AND **NOT HAVE GLOBAL SCOPE** TO MAKE SURE THERE ARE NO LOCK ISSUES

from enum import Enum
from PIL import Image
import librosa
import numpy as np
import os
import wave
import onnxruntime as ort
from datetime import datetime
from app.database.db import db_session
from app.database.models import DistressCall, FeedingPatterns, SMSAlerts
from app.alerts import send_sms_alert
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.logging_service import MultiprocessLogger

logger = MultiprocessLogger.get_logger("Mapping")

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

import librosa

# def scale_melspec(mel_spec):
#     target_size = (90, 200)
    
#     # Log-scale and clip the values
#     mel_spec = librosa.util.normalize(mel_spec)
    
#     # Clip to valid range [-1, 1]
#     mel_spec = np.clip(mel_spec, -1, 1)

#     # Replace NaNs and infs
#     mel_spec = np.nan_to_num(mel_spec, nan=0.0, posinf=1.0, neginf=-1.0)

#     # Rescale to [0, 255]
#     mel_spec = ((mel_spec + 1) / 2) * 255
#     mel_spec = mel_spec.astype(np.uint8)

#     img = Image.fromarray(mel_spec)
#     img = img.resize(target_size, Image.Resampling.LANCZOS)
#     img_array = np.array(img)

#     return img_array



    
# def predict_from_wav(Model,WAV):
#     y, sr = librosa.load(WAV)
#     mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=2048, hop_length=512, n_mels=90)
#     log_mel_spec = librosa.power_to_db(mel_spec)
#     scaled_mel_spec = scale_melspec(log_mel_spec)

#         # Shape it to model input: (1, H, W, 3)
#     input_tensor = np.repeat(scaled_mel_spec[..., np.newaxis], 3, axis=-1)
#     input_tensor = np.expand_dims(input_tensor, axis=0)

#     print("Input tensor generated")

#     print("Input shape:", input_tensor.shape)
#     print("Model input shape:", Model.input_shape)

#     prediction = Model.predict(input_tensor, verbose=1)

#     print("Prediction made")

#     pred_class = np.argmax(prediction)
#     confidence = float(np.max(prediction))
#     print("Predicted class:", pred_class, "with confidence:", confidence)
#     if pred_class == 1:
#         return Predictions.HFC, confidence
#     elif pred_class == 0:
#         return Predictions.LFC, confidence
def predict_from_wav(ModelPath, WAV):
    try:
        y, sr = librosa.load(WAV)
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=2048, hop_length=512, n_mels=90)
        log_mel_spec = librosa.power_to_db(mel_spec)
        scaled_mel_spec = scale_melspec(log_mel_spec)
        # Shape it to model input: (1, H, W, 3)
        input_tensor = np.repeat(scaled_mel_spec[..., np.newaxis], 3, axis=-1)
        input_tensor = np.expand_dims(input_tensor, axis=0).astype(np.float32)

        logger.info("Input tensor generated for model inference.")
        logger.info(f"Input shape: {input_tensor.shape}")

        # Load ONNX model and run inference
        session = ort.InferenceSession(ModelPath)
        input_name = session.get_inputs()[0].name
        logger.info(f"Model input name: {input_name}")

        prediction = session.run(None, {input_name: input_tensor})[0]

        # logger.info("Prediction made.")
        # logger.info(f"Prediction : {prediction}")
        # pred_class = np.argmax(prediction)
        # # pred_class = prediction[0]  # Assuming the model outputs a single value for binary classification
        # confidence = float(np.max(prediction))
        # logger.info(f"Predicted class: {pred_class} with confidence: {confidence}")
        # if pred_class == 1:
        #     return Predictions.HFC, confidence
        # elif pred_class == 0:
        #     return Predictions.LFC, confidence
        logger.info("Prediction made.")
        logger.info(f"Prediction : {prediction}")

        score = float(prediction[0][0])  # Probability of class 1
        pred_class = 1 if score >= 0.5 else 0
        confidence = score if pred_class == 1 else 1 - score

        logger.info(f"Predicted class: {pred_class} with confidence: {confidence:.4f}")

        if pred_class == 1:
            return Predictions.HFC, confidence
        else:
            return Predictions.LFC, confidence

    except Exception as e:
        logger.error(f"Error during model inference: {e}", exc_info=True)
        return None, None

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
# def save_raw_to_wav(raw_data, output_wav_path, sample_rate=22050):
#     with wave.open(output_wav_path, 'wb') as wf:
#         wf.setnchannels(1)        # Mono
#         wf.setsampwidth(2)         # 16 bits = 2 bytes
#         wf.setframerate(sample_rate)
#         if isinstance(raw_data, list):
#             raw_data = bytes(raw_data)
#         wf.writeframes(raw_data)

def save_raw_to_wav(raw_chunks, output_wav_path, sample_rate=22050):

    # WAV file settings — must match ESP32 recording config
    sample_rate = 22500
    sample_width = 2  # bytes (16 bits)
    channels = 1

    import base64
    try:
        # raw_bytes = map(lambda chunk: base64.b64decode(chunk), raw_chunks)
        # # Step 1: Join all chunks (strings) into one bytes object
        # # raw_bytes = b''.join(chunk.encode('latin1') for chunk in raw_chunks)
        # raw_bytes = b''.join(raw_bytes)
        raw_bytes = raw_chunks

        # Step 2: Save as WAV
        with wave.open(output_wav_path, 'wb') as wf:
            wf.setnchannels(channels)        # Mono
            wf.setsampwidth(sampwidth=sample_width)        # 16-bit PCM
            wf.setframerate(sample_rate)
            wf.writeframes(raw_bytes)

        logger.info(f"Saved raw audio to {output_wav_path}")
    except Exception as e:
        logger.error(f"Error saving raw audio to {output_wav_path}: {e}", exc_info=True)


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
    from app.alerts import _get_bovin_name_from_db

    """
    Process a batch of audio data from the microphone, run inference using ONNX model,
    and save results to the database.
    """

    # onnx_model_path = "app/models/xgb_model.onnx"
    onnx_model_path = os.getenv("BITE_CHEW_MODEL_PATH")
    logger.info(f"Using ONNX model at: {onnx_model_path}")
    # Constants
    LABELS = {0: "chew", 1: "bite", 2: "chew-bite"}

    # Main pipeline
    logger.info(f"Processing microphone batch data: {len(batch_data['data'])} messages for bovine {batch_data['data'][0]['bovine_id']}")
    db = db_session()

    try:
        predictions = []
        # print("*****", batch_data['data'])
        for message in batch_data['data']:
            bovine_id = message['bovine_id']
            logger.info(f"Processing message for Bovine {bovine_id}")
            # timestamp = datetime.strptime(message['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")  # Assume ISO format
            timestamp = message['timestamp']
            logger.info(f"Timestamp for Bovine {bovine_id}: {timestamp}")
            # Save raw audio to wav

            temp_wav_path = f"./tmp/{bovine_id}_{timestamp}.wav"
            os.makedirs("./tmp", exist_ok=True)
            logger.info("Saving raw audio to wav: %s", temp_wav_path)
    
            # message['data'] = [ chunk for chunk in sorted(message['data'], key=lambda x: x['index']) ]
            save_raw_to_wav(message['data'], temp_wav_path)
            logger.info("Saved raw audio to wav chunk: %s", temp_wav_path)

            # Inference
            logger.info("Running inference(bite-chew) on wav file: %s", temp_wav_path)
            pred = run_inference(onnx_model_path, temp_wav_path)
            logger.info("Inference result: %s", pred)

            # label_idx = int(np.argmax(pred))
            # print(label_idx)
            label = LABELS.get(pred, "unknown")

            predictions.append((timestamp, label))
            logger.info(f"Predicted label for Bovine {bovine_id} at {timestamp}: {label}")

            # Inference with Keras model (HFC / LFC)
            distress_model = os.getenv("DISTRESS_MODEL_PATH")
            frequency_class, probability = predict_from_wav(distress_model,temp_wav_path)
            logger.info(f"Distress model prediction for Bovine {bovine_id} at {timestamp}: {frequency_class}, Probability: {probability}")
            if frequency_class == Predictions.HFC: # or frequency_class  Predictions.LFC:
                distress_call = DistressCall(
                    bovine_id=bovine_id,
                    timestamp=timestamp,
                    probability=probability  # You can decide what value to store
                )
                bovine_name = _get_bovin_name_from_db(bovine_id)
                distress_message = f"Alert: Your animal, {bovine_name}, is showing signs of distress. Please check on it as soon as possible."
                send_sms_alert(distress_message, bovine_id)
            
                db.add(distress_call)

                sms_alert = SMSAlerts(
                    user_id=1,
                    bovine_id=bovine_id,
                    timestamp=timestamp,
                    message=distress_message
                )

                db.add(sms_alert)

            # Cleanup
            os.remove(temp_wav_path)
            logger.info("Removed temporary wav file: %s", temp_wav_path)

            feeding_pattern = FeedingPatterns(
                bovine_id=bovine_id,
                timestamp=timestamp,
                bite_chew=pred
            )
            db.add(feeding_pattern)
            logger.info(f"Saved feeding pattern for Bovine {bovine_id} at {timestamp}: {pred}")
            logger.info("processed audio data")
        db.commit()

        return {"status": "success", "predictions": predictions}

    except Exception as e:
        db.rollback()
        logger.error(f"Error processing microphone batch: {e.with_traceback()}", exc_info=True)
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

def accelerometer_pipeline(batch_data):
    from app.process_lamness.preprocess_lamness import predict_lameness
    from app.alerts import _get_bovin_name_from_db
    from app.database.models import LamenessInference,Bovine
    
    logger.info("Accelerometer pipeline triggered ✅")
    
    try:
        # Combine all acclerometer_data into a single list of dictionaries
        combined_data = {"acclerometer_data": []}
  
        for message in batch_data['data']:
            if 'acclerometer_data' in message:
                combined_data["acclerometer_data"].append(message['acclerometer_data'])  # append dict
            else:
                logger.warning(f"Missing 'acclerometer_data' in message: {message}")

        # print(f"Combined acclerometer_data data: {combined_data}", flush=True)

        # Extract Bovine ID and a dummy timestamp (replace with real logic if needed)
        bovine_id = batch_data['data'][0].get('bovine_id', 'unknown')
        timestamp = datetime.now().isoformat()
        logger.info(f"Processing acclerometer_data message for Bovine {bovine_id} at {timestamp}")
        
        # Predict lameness
        try:
            # print("Calling predict_lameness with data:", combined_data, flush=True)
            results = predict_lameness(combined_data)
            if results is not None and isinstance(results, dict):
                prediction = results.get("prediction")
                steps = results.get("steps")
                logger.info(f"Lameness prediction: {prediction}, Steps counted: {steps}")

                # # Update Bovine table with number of steps
                # try:
                #     from app.database.models import Bovine
                #     bovine = db_session.query(Bovine).filter_by(bovine_id=bovine_id).first()
                #     if bovine is not None and steps is not None:
                #         bovine.steps = steps  # Assumes 'steps' field exists in Bovine model
                #         db_session.commit()
                #         logger.info(f"Updated Bovine {bovine_id} with steps: {steps}")
                #     else:
                #         logger.warning(f"Could not update steps for Bovine {bovine_id}: bovine or steps missing.")
                # except Exception as e:
                #     logger.error(f"Error updating steps in Bovine table: {e}", exc_info=True)

                if prediction is not None and prediction >= 3:
                    lameness_inference = LamenessInference(
                        bovine_id=bovine_id,
                        metric=prediction,
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
                    logger.info(sms_alert)
                    db_session.add(sms_alert)
                    db_session.commit()
                else:
                    logger.info(f"Lameness prediction for Bovine {bovine_id} is below threshold: {prediction}")
                logger.info(f"Predicted lameness for Bovine {bovine_id} at {timestamp}: {prediction}, Steps: {steps}")
            else:
                logger.error(f"Invalid results from predict_lameness: {results}")
        except Exception as e:
            logger.error(f"Error in predict_lameness: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Error in accelerometer_pipeline: {e}", exc_info=True)

    return "Accelerometer pipeline complete ✅"


 


def camera_pipeline(batch_data):
    from app.process_images.crop_detect import detect_cows, batch_detect_diseases
    from app.alerts import _get_bovin_name_from_db
    from app.database.models import SkinDiseases, SMSAlerts
    from app.alerts import send_sms_alert
    from datetime import datetime

    logger.info("Camera pipeline triggered ✅")

    try:
        
        for messages in batch_data['data']:
            try:
                # Process each message in the batch
                bovine_id = messages.get('bovine_id')
                if not bovine_id:
                    logger.warning("Missing bovine_id in message")
                    continue

                logger.info("Bovine ID: %s", bovine_id)

                timestamp = datetime.strptime(messages['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
                logger.info(f"Processing camera message at {timestamp}")

                # Detect cows in the image
                detected_cows = detect_cows(messages['image_raw'])
                if not detected_cows:
                    logger.info(f"No cows detected for Bovine {bovine_id} at {timestamp}")
                    continue

                # Detect diseases in the detected cows
                diseases = batch_detect_diseases(detected_cows)
                if not diseases:
                    logger.info(f"No diseases detected for Bovine {bovine_id} at {timestamp}")
                    continue

                logger.info("Diseases detected: %s", diseases)

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
                logger.info(f"Disease inference saved for Bovine {bovine_tag}")

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
                logger.info(f"SMS alert saved for Bovine {bovine_id}")

            except Exception as e:
                db_session.rollback()
                logger.error(f"Error processing message for Bovine {bovine_id}: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Error in camera pipeline: {e}", exc_info=True)

    return "Camera pipeline triggered ✅"
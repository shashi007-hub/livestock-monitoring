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
from app.database.models import DistressCall
from app.alerts import send_sms_alert

# class Predictions(Enum):
#     HFC = "HFC"
#     LFC = "LFC"

# class fcClassifier(object):
#     Model = load_model(rf"src\ML_workspace\models\model.h5")
#     def __init__(self, FileID: str) -> None:
#         self.File = FileID
#         self.PATH = rf"./FILES/audio/{self.File}"

#     def Predict(self):
#         try:
#             frequecy = fcClassifier.predict(self.PATH)
#             return {
#                 "predictions": frequecy
#             }
#         except Exception as e:
#             print('Exception', str(e))
#             return {"error" : e}

    
#     def scale_melspec(mel_spec):
#         target_size = (90, 200)  # Target size for mel spectrograms
#         # Scale mel spectrogram using PIL
#         scaled_mel_spec = librosa.util.normalize(mel_spec)  # Normalize mel spectrogram
#         scaled_mel_spec = (scaled_mel_spec * 255).astype(np.uint8)  # Convert to uint8
#         scaled_mel_spec = Image.fromarray(scaled_mel_spec)  # Convert to PIL image
#         scaled_mel_spec = scaled_mel_spec.resize(target_size, Image.Resampling.LANCZOS)  # Resize
#         scaled_mel_spec = np.array(scaled_mel_spec)
#         print(scaled_mel_spec.shape)

#         return scaled_mel_spec
    
#     def predict(WAV):
#         scale,sr=librosa.load(WAV)
#         mel_spec=librosa.feature.melspectrogram(y=scale,sr=sr,n_fft=2048,hop_length=512,n_mels=90)
#         mel_spec=fcClassifier.scale_melspec(mel_spec)
#         #print(mel_spec.shape)
#         log_mel_spectrogram=librosa.power_to_db(mel_spec)
#         log_mel_spectrogram=np.repeat(log_mel_spectrogram[...,np.newaxis],3,axis=-1)
#         log_mel_spectrogram = np.expand_dims(log_mel_spectrogram, axis=0)
#         #print(log_mel_spectrogram.shape)

#         prediction=(fcClassifier.Model.predict(log_mel_spectrogram))
#         if prediction[0]>0.5:
#             return Predictions.HFC
#         return Predictions.LFC

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

    # frequency_classes = []

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
            print(f"Predicted label for {bovine_id} at {timestamp}: {label}", flush=True)

            # Inference with Keras model (HFC / LFC)
            # frequency_class = fcClassifier.predict(temp_wav_path)

            # if frequency_class == Predictions.HFC:
            #     distress_call = DistressCall(
            #         bovine_id=bovine_id,
            #         timestamp=datetime.utcnow(),
            #         probability=""  # You can decide what value to store
            #     )
            #     send_sms_alert("DISTRESS CALL",bovine_id)
            
            # db.add(distress_call)

            # Cleanup
            os.remove(temp_wav_path)
            print("Removed temporary wav file:", temp_wav_path, flush=True)

        # Save the result into DistressCall (or another model)
        # avg_feeding_rate = np.mean(metrics["Feeding Rates (FR)"]) if metrics["Feeding Rates (FR)"] else 0

        # distress_call = DistressCall(
        #     bovine_id=bovine_id,
        #     timestamp=datetime.utcnow(),
        #     probability=avg_feeding_rate  # You can decide what value to store
        # )

        # db.add(distress_call)
        # db.commit()

        # print(f"Saved distress call for bovine {bovine_id} with average feeding rate {avg_feeding_rate:.3f}", flush=True)

        return {"status": "success", "predictions": predictions}

    except Exception as e:
        db.rollback()
        print(f"Error processing microphone batch: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

def parse_predictions(predictions):
    SILENCE_THRESHOLD_SECONDS = 300  # 5 minutes
    # predictions = list of (timestamp, label)
    sessions = []
    current_session = []
    last_time = None

    for timestamp, label in predictions:
        if label in ['chew', 'bite', 'chew-bite']:
            if last_time and (timestamp - last_time).total_seconds() > SILENCE_THRESHOLD_SECONDS:
                if current_session:
                    sessions.append(current_session)
                current_session = []
            current_session.append((timestamp, label))
            last_time = timestamp

    if current_session:
        sessions.append(current_session)
    return sessions

def calculate_metrics(predictions):
    sessions = parse_predictions(predictions)
    total_feeding_time = timedelta()
    feeding_frequencies = len(sessions)
    meal_durations = []
    feeding_rates = []
    total_chews_bites = len(predictions)

    for session in sessions:
        start = session[0][0]
        end = session[-1][0]
        duration = end - start
        duration_minutes = duration.total_seconds() / 60.0
        meal_durations.append(duration_minutes)
        total_feeding_time += duration

        num_chews = len(session)
        if duration_minutes > 0:
            feeding_rates.append(num_chews / duration_minutes)
        else:
            feeding_rates.append(0)

    # Metrics
    FT = total_feeding_time.total_seconds() / 60.0
    FF = feeding_frequencies
    MD = meal_durations
    AFT = FT / FF if FF > 0 else 0
    IMI = []
    for i in range(len(sessions) - 1):
        gap = (sessions[i+1][0][0] - sessions[i][-1][0])
        IMI.append(gap.total_seconds() / 3600.0)  # hours
    FR = feeding_rates
    TCPD = total_chews_bites

    return {
        "Feeding Time (FT)": FT,
        "Feeding Frequency (FF)": FF,
        "Meal Durations (MD)": MD,
        "Average Feeding Time (AFT)": AFT,
        "Inter-Meal Intervals (IMI)": IMI,
        "Feeding Rates (FR)": FR,
        "Total Chews/Bites Per Day": TCPD,
    }

def metrics_for_cron_job(predictions):
    metrics = calculate_metrics(predictions)
    print("Calculated Metrics:", metrics, flush=True)
    return {
        "Date": datetime.utcnow(),
        "Bovine ID": predictions[0][0].bovine_id,
        "Metrics":metrics
        }

def accelerometer_pipeline(batch_data):
    pass

def camera_pipeline(batch_data):
    pass


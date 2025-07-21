from process_images.preprocess_images import decode_base64_image, filter_Detections, rescale_back
from process_images.check import check_onnx_model
import onnxruntime as ort
import numpy as np
import cv2
from PIL import Image
import easyocr
import os
import joblib
from dotenv import load_dotenv
from app.logging_service import MultiprocessLogger

load_dotenv()
logger = MultiprocessLogger.get_logger(__name__)

def detect_cows(image):
    try:
        from process_images.preprocess_images import decode_base64_image, filter_Detections, rescale_back
    except Exception as e:
        logger.error(f"Import error: {e}")
        return []

    try:
    #     logger.info("Loading ONNX model for cow detection...")
    #     scaler_filename = "app/models/yolo11n.onnx"
    #     if not os.path.exists(scaler_filename):
    #         logger.warning(f"The file '{scaler_filename}' does not exist.")
    #         return []

    #     ort_session = ort.InferenceSession(scaler_filename, providers=["CPUExecutionProvider"])
    #     logger.info("ONNX model loaded")
        ort_session = check_onnx_model()
        if ort_session is None: 
            logger.error("Failed to load ONNX model")
            return []
        logger.info("ONNX model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading ONNX model: {e}")
        return []

    try:
        image_data = decode_base64_image(image)
        if image_data is None:
            logger.error("Decoded image is None")
            return []
        logger.info("image_data decoded")
    except Exception as e:
        logger.error(f"Error decoding image: {e}")
        return []

    try:
        img_w, img_h = image_data.shape[1], image_data.shape[0]
        logger.info(f"Image width: {img_w}, Image height: {img_h}")
        img = cv2.resize(image_data, (640, 640))
        logger.info("image resized")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        logger.info("image converted to RGB")
        img = img.transpose(2, 0, 1)
        logger.info("image transposed")
        img = img.reshape(1, 3, 640, 640)
        logger.info("image reshaped")
        img = img / 255.0
        img = img.astype(np.float32)
        logger.info("image preprocessed")
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        return []

    try:
        outputs = ort_session.run(None, {"images": img})
        results = outputs[0]
        logger.info("ONNX model inference done")
    except Exception as e:
        logger.error(f"Error during ONNX inference: {e}")
        return []

    try:
        results = results.transpose()
        results = filter_Detections(results)
        logger.info("detections filtered")
        rescaled_results, confidences = rescale_back(results, img_w, img_h)
        logger.info(f"Confidence scores: {confidences}")
        logger.info("cows detected")
    except Exception as e:
        logger.error(f"Error processing detection results: {e}")
        return []

    cropped_images = []
    idx = 0
    try:
        for res, conf in zip(rescaled_results, confidences):
            x1, y1, x2, y2, cls_id = res
            cls_id = int(cls_id)
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # cropped_image = image[y1:y2, x1:x2]
            cropped_image = image_data[y1:y2, x1:x2]

            # cropped_image_pil = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
            cropped_image_pil = Image.fromarray(cropped_image)
            cropped_images.append(cropped_image_pil)
            # save_path = f"cropped_image_{idx + 1}.jpg"
            # cropped_image_pil.save(save_path)
            idx += 1
            # logger.info(f"Cropped image saved at: {save_path}")    
    except Exception as e:
        logger.error(f"Error cropping images: {e}")

    return cropped_images


def read_tag(cow_crop):
    try:
        logger.info("Reading tag number...")
        reader = easyocr.Reader(['en'])
        cow_crop_np = np.array(cow_crop)
        result = reader.readtext(cow_crop_np)
    except Exception as e:
        logger.error(f"Error reading tag: {e}")
        return None

    best_tag = None
    max_confidence = 0.0
    try:
        for (bbox, text, prob) in result:
            if any(char.isdigit() for char in text):
                logger.info(f"Detected tag: {text} (Confidence: {prob:.2f})")
                if prob > max_confidence:
                    max_confidence = prob
                    best_tag = text
    except Exception as e:
        logger.error(f"Error processing OCR results: {e}")

    if best_tag is not None:
        logger.info(f"Returning tag with highest confidence: {best_tag} (Confidence: {max_confidence:.2f})")
    else:
        logger.info("No valid tag number detected.")

    return best_tag


def preprocess_image(image):
    try:
        image = image.resize((224, 224))
        image = np.array(image).astype(np.float32) / 255.0
        image = (image - 0.5) / 0.5
        image = image.transpose(2, 0, 1)
        return np.expand_dims(image, axis=0)
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        return None


def batch_detect_diseases(cow_crops):

    try:
        logger.info("Detecting diseases...")
        if not cow_crops:
            return []

        results = []
        for idx, cow_crop in enumerate(cow_crops):
            input_image = preprocess_image(cow_crop)
            if input_image is None:
                logger.warning(f"Skipping cow crop {idx + 1} due to preprocessing error")
                continue
            disease_model = os.getenv("DISEASE_DETECTION_MODEL_PATH")
            session = ort.InferenceSession(disease_model, providers=["CPUExecutionProvider"])
            outputs = session.run(None, {"input": input_image})
            logits = outputs[0]
            probs = 1 / (1 + np.exp(-logits))
            pred = (probs > 0.5).astype(int)
            class_names = ["BRD", "Bovine", "Contagious", "Disease", "Ecthym", "Respiratory","Unlabelled", "Healthy", "Lumpy","Skin"]
            diseased_labels = [class_names[i] for i in range(len(class_names)) if pred[0][i] == 1 and class_names[i] not in ["Healthy", "Skin", ""]]
            logger.info(f"Predicted labels for cow {idx + 1}: {diseased_labels}")
            if diseased_labels:
                cow_tag = read_tag(cow_crop)
                results.append({
                    "Bovine_tag": cow_tag,
                    "disease_status": diseased_labels,
                    "image": cow_crop
                })
                logger.info(f"Detected diseases for cow {idx + 1}: {diseased_labels}")
        return results
    except Exception as e:
        logger.error(f"Error in batch_detect_diseases: {e}")
        return []
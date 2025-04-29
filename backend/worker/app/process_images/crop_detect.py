from .preprocess_images import decode_base64_image, filter_Detections,rescale_back
import onnxruntime as ort
import numpy as np
import cv2
from PIL import Image
import easyocr

# Load the ONNX model using onnxruntime



def detect_cows(image):
    print("Loading ONNX model for cow detection...")
    ort_session = ort.InferenceSession("app/models/yolo11n.onnx")
    print("Detecting cows...")
    print("onnx_model loaded")

    image_data = decode_base64_image(image)
    print("image_data decoded")
    
    img_w, img_h = image_data.shape[1], image.shape[0]

    img = cv2.resize(image_data, (640, 640))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.transpose(2, 0, 1)
    img = img.reshape(1, 3, 640, 640)

    img = img / 255.0

# Convert image to float32
    img = img.astype(np.float32)

    outputs = ort_session.run(None, {"images": img})
    results = outputs[0]
    results = results.transpose()
    results = filter_Detections(results)
    print("detections filtered")
    rescaled_results, confidences = rescale_back(results, img_w, img_h)
    print("cows detected")
    cropped_images = []  

    for res, conf in zip(rescaled_results, confidences):
        x1, y1, x2, y2, cls_id = res
        cls_id = int(cls_id)
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        # Crop the image using bounding box coordinates
        cropped_image = image[y1:y2, x1:x2]  

        # Convert the cropped image to PIL Image, ensuring correct color format
        cropped_image_pil = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))

        # Append the cropped image to the list
        cropped_images.append(cropped_image_pil)  

    return cropped_images



def read_tag(cow_crop):
    """
    Reads the tag number from the cropped cow image using OCR.
    """
    print("Reading tag number...")
    best_tag = None
    max_confidence = 0.0


    reader = easyocr.Reader(['en'])
    cow_crop_np = np.array(cow_crop)

    
    result = reader.readtext(cow_crop_np)
    for (bbox, text, prob) in result:
        # Check if the detected text contains any digits
        if any(char.isdigit() for char in text):
            print(f"Detected tag: {text} (Confidence: {prob:.2f})")
            if prob > max_confidence:
                max_confidence = prob
                best_tag = text

    if best_tag != None:
        print(f"Returning tag with highest confidence: {best_tag} (Confidence: {max_confidence:.2f})")
    else:
        print("No valid tag number detected.")

    return best_tag
def preprocess_image(image):
    """
    Preprocess a PIL image for ONNX model inference.
    """
    image = image.resize((224, 224))  # Resize to model input size
    image = np.array(image).astype(np.float32) / 255.0  # Normalize to [0, 1]
    image = (image - 0.5) / 0.5  # Apply normalization (mean=0.5, std=0.5)
    image = image.transpose(2, 0, 1)  # Convert to CHW format
    return np.expand_dims(image, axis=0)  # Add batch dimension

def batch_detect_diseases(cow_crops):
    """
    Detects diseases in a list of cropped cow images (PIL images).
    Only returns diseased cows (excludes healthy ones).

    Args:
        cow_crops: List of cropped cow images (PIL Images).

    Returns:
        List of dictionaries with:
        - 'Bovine_tag': the cow tag detected from the image
        - 'disease_status': list of detected diseases (excluding 'Healthy')
        - 'image': the corresponding PIL cropped image
    """
    print("Detecting diseases...")
    if not cow_crops:
        return []

    results = []
    for idx, cow_crop in enumerate(cow_crops):
        # Preprocess the image
        input_image = preprocess_image(cow_crop)

        # Run inference
        outputs = session.run(None, {"input": input_image})
        logits = outputs[0]  # Get the logits from the ONNX model

        # Apply sigmoid and threshold
        probs = 1 / (1 + np.exp(-logits))  # Sigmoid function
        pred = (probs > 0.5).astype(int)

        # Get disease labels
        labels = [class_names[i] for i in range(len(class_names)) if pred[0][i] == 1]
        diseased_labels = [label for label in labels if label != "Healthy" and label != "Skin" and label != ""]

        if diseased_labels:
            cow_tag = read_tag(cow_crop)  # Get the cow tag using the read_tag function
            results.append({
                "Bovine_tag": cow_tag,
                "disease_status": diseased_labels,
                "image": cow_crop
            })
            print(f"Detected diseases for cow {idx + 1}: {diseased_labels}")

    return results
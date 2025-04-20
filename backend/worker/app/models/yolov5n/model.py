import cv2
import numpy as np
from ..model_interface import ONNXModel
from PIL import Image

class YOLOv5n(ONNXModel):
    def __init__(self, model_path: str):
        """Initialize YOLOv5n model.

        Args:
            model_path (str): Path to YOLOv5n ONNX model file
        """
        super().__init__(model_path)
        self.input_size = (640, 640)  # Default YOLOv5n input size
        self.conf_threshold = 0.1   # Confidence threshold
        self.iou_threshold = 0.45     # NMS IoU threshold

    def preprocess(self, image_path: str):
        """Preprocess the input image for YOLOv5n inference.

        Args:
            image_path: Path to the input image

        Returns:
            dict: Dictionary with preprocessed input tensor
        """
        # Load image from path
        pil_image = Image.open(image_path)

        # Convert to numpy array (H, W, C)
        input_data = np.array(pil_image)


        # Convert BGR to RGB
        input_data = cv2.cvtColor(input_data, cv2.COLOR_BGR2RGB)

        # Resize image
        image = cv2.resize(input_data, self.input_size)

        # Normalize pixel values and transpose
        image = image.astype(np.float32) / 255.0
        image = np.transpose(image, (2, 0, 1))  # HWC to CHW
        image = np.expand_dims(image, axis=0)    # Add batch dimension

        return {self.session.get_inputs()[0].name: image}

    def postprocess(self, outputs: dict):
        # return outputs
        """Postprocess YOLOv5n output to get detections.

        Args:
            outputs (dict): Model outputs containing predictions

        Returns:
            list: List of detections, each in format [x1, y1, x2, y2, confidence, class_id]
        """
        # Get predictions from output
        predictions = next(iter(outputs.values()))  # Shape: (1, num_boxes, xywh+conf+num_classes)

        # Process predictions
        predictions = predictions[0]  # Remove batch dimension

        # Filter by confidence
        mask = predictions[:, 4] > self.conf_threshold
        predictions = predictions[mask]

        if len(predictions) == 0:
            return []

        # Get boxes (xywh to xyxy)
        boxes = predictions[:, :4].copy()
        boxes[:, 0] -= boxes[:, 2] / 2  # x1 = x - w/2
        boxes[:, 1] -= boxes[:, 3] / 2  # y1 = y - h/2
        boxes[:, 2] += boxes[:, 0]      # x2 = x1 + w
        boxes[:, 3] += boxes[:, 1]      # y2 = y1 + h

        # Get scores and classes
        scores = predictions[:, 4]
        class_ids = np.argmax(predictions[:, 5:], axis=1)

        # Apply NMS
        indices = cv2.dnn.NMSBoxes(
            boxes.tolist(),
            scores.tolist(),
            self.conf_threshold,
            self.iou_threshold
        )

        if len(indices) == 0:
            return []

        # Format output
        detections = []
        for idx in indices:
            if isinstance(idx, list):  # Handle different OpenCV versions
                idx = idx[0]
            detections.append([
                *boxes[idx],           # x1, y1, x2, y2
                scores[idx],           # confidence
                class_ids[idx]         # class_id
            ])

        return np.array(detections)
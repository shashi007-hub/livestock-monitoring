import os
from dotenv import load_dotenv
from app.logging_service import MultiprocessLogger

load_dotenv()
logger = MultiprocessLogger.get_logger(__name__)


def check_onnx_model():
    scaler_filename = os.getenv("COW_DETECTION_MODEL_PATH")
    if not os.path.exists(scaler_filename):
        logger.error(f"The file '{scaler_filename}' does not exist.")
    else:
        logger.info(f"The file '{scaler_filename}' exists.")
        # Load the ONNX model
        try:
            import onnxruntime as ort
            ort_session = ort.InferenceSession(scaler_filename, providers=["CPUExecutionProvider"])
            logger.info("ONNX model loaded")
            return ort_session
        except Exception as e:
            logger.error(f"Error loading ONNX model: {e}")

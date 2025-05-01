import os

def check_onnx_model():
    scaler_filename = "../app/models/yolo11n.onnx"
    if not os.path.exists(scaler_filename):
        print(f"The file '{scaler_filename}' does not exist.")
    else:
        print(f"The file '{scaler_filename}' exists.")
        # Load the ONNX model
        try:
            import onnxruntime as ort
            ort_session = ort.InferenceSession(scaler_filename, providers=["CPUExecutionProvider"])
            print("ONNX model loaded")
            return ort_session
        except Exception as e:
            print(f"Error loading ONNX model: {e}")    
            
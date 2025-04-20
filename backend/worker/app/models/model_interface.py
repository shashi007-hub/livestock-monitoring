from abc import ABC, abstractmethod
import numpy as np
import onnxruntime as ort

class ONNXModel(ABC):
    """Abstract base class for ONNX Runtime models."""

    def __init__(self, model_path: str):
        """Initialize the ONNX model.

        Args:
            model_path (str): Path to the ONNX model file
        """
        self.model_path = model_path
        self.session = None
        self._initialize_session()

    def _initialize_session(self):
        """Initialize ONNX Runtime inference session."""
        try:
            self.session = ort.InferenceSession(self.model_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load ONNX model: {str(e)}")

    @abstractmethod
    def preprocess(self, input_data: any):
        """Preprocess the input data before inference.

        Args:
            input_data: Raw input data

        Returns:
            dict: Dictionary containing preprocessed input tensors
        """
        pass

    @abstractmethod
    def postprocess(self, outputs: dict):
        """Postprocess the model outputs.

        Args:
            outputs (dict): Raw model outputs

        Returns:
            Processed results in the required format
        """
        pass

    def predict(self, input_data: any):
        """Run inference on the input data.

        Args:
            input_data: Input data to run inference on

        Returns:
            Processed model output
        """
        if self.session is None:
            raise RuntimeError("Model session not initialized")

        # Preprocess input data
        inputs = self.preprocess(input_data)

        # Run inference
        outputs = self.session.run(None, inputs)

        # return outputs

        # Convert outputs to dictionary
        output_names = [output.name for output in self.session.get_outputs()]
        outputs_dict = dict(zip(output_names, outputs))

        # Postprocess results
        return self.postprocess(outputs_dict)

    def get_input_details(self):
        """Get model input details."""
        return self.session.get_inputs()

    def get_output_details(self):
        """Get model output details."""
        return self.session.get_outputs()
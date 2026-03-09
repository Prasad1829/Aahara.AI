import os

import tensorflow as tf

# Global model variable
_model = None
_image_size = (224, 224)  # Default/fallback model input size
_model_filenames = [
    "foodvision_model.keras",
    "food_c101_n1000_r384x384x3.h5",
]


def _get_candidate_model_paths():
    # project_dir points to: .../ingredient_recipe_ai
    project_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )
    workspace_dir = os.path.abspath(os.path.join(project_dir, ".."))

    candidate_paths = []
    for filename in _model_filenames:
        candidate_paths.append(os.path.join(project_dir, "dataset", "models", filename))
        candidate_paths.append(os.path.join(workspace_dir, filename))
    return candidate_paths


def get_model():
    global _model, _image_size
    if _model is None:
        candidate_paths = _get_candidate_model_paths()
        model_path = next((path for path in candidate_paths if os.path.exists(path)), None)

        if model_path is None:
            checked_paths = "\n".join(f"- {path}" for path in candidate_paths)
            raise FileNotFoundError(f"Model file not found. Checked:\n{checked_paths}")

        print(f"Loading model from: {model_path}")

        try:
            _model = tf.keras.models.load_model(model_path, compile=False)
            if hasattr(_model, "input_shape") and _model.input_shape and len(_model.input_shape) >= 3:
                _image_size = (int(_model.input_shape[1]), int(_model.input_shape[2]))
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise e

    return _model

def get_image_size():
    return _image_size

def get_preprocess_function():
    # Simple normalization for this model: pixel values / 255.0
    def preprocess(img):
        return img / 255.0
    return preprocess

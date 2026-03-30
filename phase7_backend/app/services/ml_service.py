import tensorflow as tf
import numpy as np
import os
import json
from app.services.cnn_preprocessing import preprocess_for_cnn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../phase4_cnn_model"))
WEIGHTS_PATH = os.path.join(MODEL_DIR, "ingredient_weights.weights.h5")
MODEL_CANDIDATES = [
    os.path.join(MODEL_DIR, "ingredient_model.keras"),
    os.path.join(MODEL_DIR, "ingredient_model.h5"),
]
CLASS_NAMES_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "../../../phase4_cnn_model/class_names.json")
)

DEFAULT_CLASS_NAMES = [
    "apple",
    "banana",
    "cabbage",
    "capsicum",
    "carrot",
    "cauliflower",
    "corn",
    "cucumber",
    "eggplant",
    "garlic",
    "ginger",
    "grapes",
    "lemon",
    "mango",
    "onion",
    "orange",
    "peas",
    "potato",
    "tomato",
    "watermelon",
]


def load_class_names():
    if os.path.exists(CLASS_NAMES_PATH):
        with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
            names = json.load(f)
            if isinstance(names, list) and names:
                return names
    return DEFAULT_CLASS_NAMES


def resolve_model_path():
    for candidate in MODEL_CANDIDATES:
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(
        "Model file not found. Put ingredient_model.keras or ingredient_model.h5 in "
        f"{MODEL_DIR}"
    )


def build_fallback_model(num_classes):
    base = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights=None,
    )
    base.trainable = False

    model = tf.keras.Sequential(
        [
            tf.keras.layers.Rescaling(1.0 / 255),
            base,
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dropout(0.25),
            tf.keras.layers.Dense(num_classes, activation="softmax"),
        ]
    )
    model.build((None, 224, 224, 3))
    return model


def load_model_with_fallback(model_path, num_classes):
    # Best path: explicit weights-only file saved from Colab.
    if os.path.exists(WEIGHTS_PATH):
        print(f"[ml_service] Loading weights-only model from: {WEIGHTS_PATH}")
        model = build_fallback_model(num_classes)
        model.load_weights(WEIGHTS_PATH)
        return model

    # Otherwise try direct full-model load.
    try:
        print(f"[ml_service] Loading full model from: {model_path}")
        return tf.keras.models.load_model(model_path, compile=False)
    except Exception as load_err:
        # Hard-fail here to avoid silently running with wrong weights/mappings.
        raise RuntimeError(
            "Model load failed. Create and place "
            f"'ingredient_weights.weights.h5' in {MODEL_DIR}. "
            f"Original error: {load_err}"
        ) from load_err


class_names = load_class_names()
resolved_model_path = resolve_model_path()

# Load model once (very important)
model = load_model_with_fallback(resolved_model_path, len(class_names))



def predict_ingredient(image_path):

    processed_image = preprocess_for_cnn(image_path)

    predictions = model.predict(processed_image, verbose=0)[0]

    predicted_index = int(np.argmax(predictions))
    confidence = float(np.max(predictions))

    top_indices = np.argsort(predictions)[::-1][:3]
    top_predictions = []
    for i in top_indices:
        confidence_value = round(float(predictions[int(i)]), 2)
        if confidence_value <= 0:
            continue
        top_predictions.append(
            {
                "ingredient": class_names[int(i)],
                "confidence": confidence_value,
            }
        )

    return {
        "ingredient": class_names[predicted_index],
        "confidence": round(confidence, 2),
        "top_predictions": top_predictions,
    }

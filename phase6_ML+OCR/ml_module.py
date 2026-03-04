import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
tf.get_logger().setLevel("ERROR")


# ── Paths ─────────────────────────────────────────────────────────────────────

BASE_DIR    = os.path.dirname(__file__)
WEIGHTS_PATH     = os.path.join(BASE_DIR, "ingredient.weights.h5")
CLASS_NAMES_PATH = os.path.join(BASE_DIR, "..", "phase4_cnn_model", "class_names.json")


# ── Load class names ──────────────────────────────────────────────────────────

if not os.path.exists(CLASS_NAMES_PATH):
    raise FileNotFoundError(f"class_names.json not found: {CLASS_NAMES_PATH}")

with open(CLASS_NAMES_PATH, "r") as f:
    class_names = json.load(f)


# ── Build model ───────────────────────────────────────────────────────────────

base = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet"
)
base.trainable = False

model = tf.keras.Sequential([
    tf.keras.layers.Rescaling(1./255),
    base,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(256, activation="relu"),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(len(class_names), activation="softmax"),
])


# ── Load weights ──────────────────────────────────────────────────────────────

if not os.path.exists(WEIGHTS_PATH):
    raise FileNotFoundError(f"ingredient.weights.h5 not found: {WEIGHTS_PATH}")

model.build((None, 224, 224, 3))
model.load_weights(WEIGHTS_PATH)
print("ML Model Loaded Successfully")


# ── Prediction ────────────────────────────────────────────────────────────────

CONFIDENCE_THRESHOLD = 0.95

def predict_ingredient(image_path: str) -> dict:
    if not os.path.exists(image_path):
        return {
            "status": "error",
            "ingredient": None,
            "confidence": 0.0,
            "message": f"File not found: {image_path}"
        }

    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)

    pred = model.predict(img_array, verbose=0)
    idx  = int(np.argmax(pred))
    conf = float(np.max(pred))

    if conf < CONFIDENCE_THRESHOLD:
        return {
            "status": "low_confidence",
            "ingredient": None,
            "confidence": round(conf * 100, 2),
            "message": f"Confidence too low: {round(conf * 100, 2)}% (need 95%+)"
        }

    return {
        "status": "success",
        "ingredient": class_names[idx],
        "confidence": round(conf * 100, 2),
        "message": "Ingredient detected successfully"
    }
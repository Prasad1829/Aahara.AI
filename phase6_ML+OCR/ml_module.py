import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image

tf.get_logger().setLevel("ERROR")

BASE_DIR = os.path.dirname(__file__)

WEIGHTS_PATH = os.path.join(BASE_DIR, "ingredient.weights.h5")

# Correct class order (from train_ds.class_names)
class_names = [
    'apple', 'banana', 'cabbage', 'capsicum', 'carrot',
    'cauliflower', 'corn', 'cucumber', 'eggplant', 'garlic',
    'ginger', 'grapes', 'lemon', 'mango', 'onion',
    'orange', 'peas', 'potato', 'tomato', 'watermelon'
]

# ---------------- Build model ----------------
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
    tf.keras.layers.Dense(len(class_names), activation="softmax")
])

# ---------------- Load weights ----------------
if not os.path.exists(WEIGHTS_PATH):
    print("ingredient.weights.h5 not found inside phase6_ML+OCR folder!")
    exit()

model.build((None, 224, 224, 3))
model.load_weights(WEIGHTS_PATH)

print("ML Model Loaded Successfully")


# ---------------- Prediction function ----------------
def predict_ingredient(image_path):
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)

    pred = model.predict(img_array, verbose=0)

    idx = int(np.argmax(pred))
    conf = float(np.max(pred))

    return class_names[idx], conf

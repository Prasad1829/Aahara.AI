import tensorflow as tf
import numpy as np
import os
from tensorflow.keras.preprocessing import image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WEIGHTS_PATH = os.path.join(BASE_DIR, "ingredient.weights.h5")
TEST_IMAGE = os.path.join(BASE_DIR, "test.jpg")

class_names = [
    'apple', 'banana', 'cabbage', 'capsicum', 'carrot',
    'cauliflower', 'corn', 'cucumber', 'eggplant', 'garlic',
    'ginger', 'grapes', 'lemon', 'mango', 'onion',
    'orange', 'peas', 'potato', 'tomato', 'watermelon'
]

# Build same model
base = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet"
)
base.trainable = False

model = tf.keras.Sequential([
    tf.keras.layers.Rescaling(1./255),   # keep only if training used this
    base,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(256, activation="relu"),
    tf.keras.layers.Dense(len(class_names), activation="softmax")
])

print("Weights exists:", os.path.exists(WEIGHTS_PATH))

model.build((None, 224, 224, 3))
model.load_weights(WEIGHTS_PATH)
print("Weights loaded")

# Save model in same folder
save_path = os.path.join(BASE_DIR, "ingredient_model.keras")
model.save(save_path)
print("Model saved at:", save_path)

# Check test image
if not os.path.exists(TEST_IMAGE):
    print("Put test.jpg inside:", BASE_DIR)
    exit()

img = image.load_img(TEST_IMAGE, target_size=(224, 224))
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0)

pred = model.predict(img_array)

idx = np.argmax(pred)
conf = float(np.max(pred)) * 100

print("Predicted:", class_names[idx])
print("Confidence:", round(conf, 2), "%")

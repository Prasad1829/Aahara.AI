import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions

print("Loading MobileNetV2 model...")

# Load pretrained model
model = MobileNetV2(weights="imagenet")

print("Model loaded successfully ✅")

# Get current folder
current_dir = os.path.dirname(os.path.abspath(__file__))

# List files in folder
files = os.listdir(current_dir)
print("Files inside folder:", files)

# Find first image file automatically
image_path = None

for file in files:
    if file.lower().endswith((".jpg", ".jpeg", ".png")):
        image_path = os.path.join(current_dir, file)
        break

if image_path is None:
    print("❌ No image file found in folder!")
    exit()

print("Using image:", image_path)

# Read image
img = cv2.imread(image_path)

if img is None:
    print("❌ Unable to read image file.")
    exit()

# Resize for MobileNet
img = cv2.resize(img, (224, 224))
img = np.expand_dims(img, axis=0)
img = preprocess_input(img)

# Predict
predictions = model.predict(img)
decoded = decode_predictions(predictions, top=1)

print("\n🎯 Prediction Result:")
print("Detected Object:", decoded[0][0][1])
print("Confidence:", round(decoded[0][0][2] * 100, 2), "%")


#python ml_test.py

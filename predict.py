import tensorflow as tf
import numpy as np
import cv2

# Load trained model
model = tf.keras.models.load_model("ingredient_model.keras")

# Automatically get class names from dataset
dataset = tf.keras.utils.image_dataset_from_directory(
    "dataset",
    image_size=(224, 224),
    batch_size=8
)

class_names = dataset.class_names
print("Class order:", class_names)

# Path of test image
image_path = "test_images/imgt33.jpeg"   # 👈 change image name here if needed

# Read image
image = cv2.imread(image_path)

if image is None:
    print("❌ Test image not found!")
    exit()

# 🔥 IMPORTANT FIX → Convert BGR to RGB
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Resize to model input size
image = cv2.resize(image, (224, 224))

# Normalize
image = image / 255.0

# Add batch dimension
image = np.expand_dims(image, axis=0)

# Predict
prediction = model.predict(image)

predicted_index = np.argmax(prediction)
predicted_class = class_names[predicted_index]
confidence = prediction[0][predicted_index] * 100

print("Prediction:", predicted_class)
print(f"Confidence: {confidence:.2f}%")

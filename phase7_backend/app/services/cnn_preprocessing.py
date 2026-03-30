import cv2
import numpy as np

def preprocess_for_cnn(image_path):

    # Read image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image not found: " + image_path)

    # Convert BGR → RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Resize to model input size
    img = cv2.resize(img, (224, 224))

    # Normalize (IMPORTANT – must match training)
    img = img.astype(np.float32)

    # Add batch dimension
    img = np.expand_dims(img, axis=0)

    return img

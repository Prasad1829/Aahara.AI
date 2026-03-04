import cv2

def preprocess_image(image_path):
    image = cv2.imread(image_path)

    # Resize to 224x224 (standard CNN input)
    image = cv2.resize(image, (224, 224))

    # Normalize pixel values (0–1)
    image = image / 255.0

    return image
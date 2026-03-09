import cv2
import os
import numpy as np

# Input & Output folders
input_path = "images/image_test.jpg"
output_folder = "processed_images"

# Create folder if not exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 1️⃣ Load Image
image = cv2.imread(input_path)

if image is None:
    print("Image not found!")
    exit()

print("Image Loaded Successfully!")

# 2️⃣ Resize to 224x224
resized = cv2.resize(image, (224, 224))

# 3️⃣ Convert to Grayscale
gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

# 4️⃣ Noise Removal (Blur)
blur = cv2.GaussianBlur(gray, (5, 5), 0)

# 5️⃣ Thresholding (Improve clarity)
_, threshold = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY)

# 6️⃣ Normalize pixel values (0-1)
normalized = threshold / 255.0

# Save images
cv2.imwrite(os.path.join(output_folder, "resized.jpg"), resized)
cv2.imwrite(os.path.join(output_folder, "gray.jpg"), gray)
cv2.imwrite(os.path.join(output_folder, "blur.jpg"), blur)
cv2.imwrite(os.path.join(output_folder, "threshold.jpg"), threshold)

print("All Preprocessed Images Saved Successfully!")

cv2.imshow("Final Processed Image", threshold)
cv2.waitKey(0)
cv2.destroyAllWindows()

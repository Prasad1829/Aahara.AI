import cv2
import os
import numpy as np

image_path = "sample.jpg"
output_folder = "processed_images"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

image = cv2.imread(image_path)

if image is None:
    print("❌ Image not found!")
    exit()

print("✅ Image Loaded")

# 1️⃣ Resize
resized = cv2.resize(image, (224, 224))

# 2️⃣ Grayscale
gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

# 3️⃣ Blur
blur = cv2.GaussianBlur(gray, (5, 5), 0)

# 4️⃣ Threshold
_, thresh = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY)

# 5️⃣ Normalize
normalized = thresh / 255.0

print("Pixel range after normalization:")
print("Min:", np.min(normalized))
print("Max:", np.max(normalized))

# Save images
cv2.imwrite(os.path.join(output_folder, "1_resized.jpg"), resized)
cv2.imwrite(os.path.join(output_folder, "2_gray.jpg"), gray)
cv2.imwrite(os.path.join(output_folder, "3_blur.jpg"), blur)
cv2.imwrite(os.path.join(output_folder, "4_threshold.jpg"), thresh)

print("✅ Preprocessed images saved")

# -------------------------
# SHOW IMAGES
# -------------------------

cv2.imshow("Original Image", image)
cv2.imshow("Resized Image", resized)
cv2.imshow("Grayscale Image", gray)
cv2.imshow("Blur Image", blur)
cv2.imshow("Threshold Image", thresh)

cv2.waitKey(0)
cv2.destroyAllWindows()



#python test_ocr.py

import cv2
import os

input_path = "phase3_preprocessing/input_images/prabhas salaar.jpg"
output_folder = "phase3_preprocessing/preprocess_images"
os.makedirs(output_folder, exist_ok=True)

img = cv2.imread(input_path)

if img is None:
    print("Image not found:", input_path)
    exit()

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply Gaussian Blur
blur = cv2.GaussianBlur(gray, (5, 5), 0)

# Apply Adaptive Threshold
thresh = cv2.adaptiveThreshold(
    blur, 255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY,
    11, 2
)

out_path = os.path.join(output_folder, "processed.jpg")
cv2.imwrite(out_path, thresh)

print("Saved in:", out_path)
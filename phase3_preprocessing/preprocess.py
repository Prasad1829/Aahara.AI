import cv2
import os

input_path = "phase3_preprocessing/input_images/prabhas salaar.jpg"
output_folder = "phase3_preprocessing/preprocess_images"

os.makedirs(output_folder, exist_ok=True)

img = cv2.imread(input_path)

if img is None:
    print("Image not found:", input_path)
    exit()

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

out_path = os.path.join(output_folder, "gray.jpg")
cv2.imwrite(out_path, gray)

print("Saved in:", out_path)

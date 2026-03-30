import cv2
from PIL import Image
import os
# 1) Get current script folder safely
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2) Input + Output paths
input_path = os.path.join(BASE_DIR, "input_images", "bike.jpg")
output_folder = os.path.join(BASE_DIR, "output_images")

# 3) Create output folder if not exists
os.makedirs(output_folder, exist_ok=True)

# 4) Read image using OpenCV
img_cv = cv2.imread(input_path)

# 5) Check if image loaded
if img_cv is None:
    print("Image not found. Check the path:", input_path)
    exit()

print("OpenCV image loaded:", img_cv.shape)

# 6) Convert BGR -> Grayscale
gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

# 7) Save grayscale image
gray_path = os.path.join(output_folder, "sample_gray.jpg")
cv2.imwrite(gray_path, gray)
print("Saved grayscale image:", gray_path)

# 8) Save as PNG (JPG -> PNG conversion)
png_path = os.path.join(output_folder, "sample_converted.png")
cv2.imwrite(png_path, img_cv)
print("Saved PNG image:", png_path)
print("\ All outputs saved inside:", output_folder)

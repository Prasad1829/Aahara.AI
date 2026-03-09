import cv2
import pytesseract
import numpy as np
import re
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

image_path = "images/biscuit.jpeg"

if not os.path.exists("processed_images"):
    os.makedirs("processed_images")

image = cv2.imread(image_path)

if image is None:
    print("Image not found")
    exit()

# Preprocessing
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
gray = cv2.convertScaleAbs(gray, alpha=1.8, beta=20)
blur = cv2.GaussianBlur(gray, (5,5), 0)
_, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

cv2.imwrite("processed_images/processed.png", thresh)

# OCR
custom_config = r'--oem 3 --psm 4 -l eng'
text = pytesseract.image_to_string(thresh, config=custom_config)

print("\n========== RAW OCR TEXT ==========\n")
print(text)

# -----------------------------
# SMART INGREDIENT EXTRACTION
# -----------------------------

lines = text.lower().split("\n")

food_keywords = [
    "flour", "sugar", "salt", "milk", "oil",
    "butter", "wheat", "maida", "starch",
    "cheese", "yeast", "powder", "spice"
]

ingredient_lines = []

for line in lines:
    for word in food_keywords:
        if word in line:
            ingredient_lines.append(line)
            break

# Join detected lines
ingredient_text = " ".join(ingredient_lines)

# Clean text
ingredient_text = re.sub(r'[^a-zA-Z,()\-\s]', '', ingredient_text)
ingredient_text = re.sub(r'\s+', ' ', ingredient_text)

ingredients = [item.strip() for item in ingredient_text.split(",") if len(item.strip()) > 2]

print("\n✅ FINAL INGREDIENTS LIST:\n")
for item in ingredients:
    print("-", item)

# Save
with open("processed_images/final_ingredients.txt", "w", encoding="utf-8") as f:
    for item in ingredients:
        f.write(item + "\n")

print("\n✔ OCR completed successfully.")

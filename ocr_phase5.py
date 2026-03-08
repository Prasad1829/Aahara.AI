import cv2
import pytesseract
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import re

# Set Tesseract path (change only if different in your system)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Hide tkinter window
Tk().withdraw()

# Select image
file_path = askopenfilename(title="Select Packaged Food Image")

# Read image
image = cv2.imread(file_path)

# Resize image (helps OCR accuracy)
image = cv2.resize(image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply slight blur to remove noise
gray = cv2.GaussianBlur(gray, (5, 5), 0)

# Adaptive threshold (better for text)
thresh = cv2.adaptiveThreshold(
    gray,
    255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY,
    11,
    2
)

# Extract text using Tesseract
custom_config = r'--oem 3 --psm 6'
text = pytesseract.image_to_string(thresh, config=custom_config)

print("\n📄 Raw Extracted Text:\n")
print(text)

# Clean text (remove unwanted characters except letters, numbers, comma)
clean_text = re.sub(r'[^a-zA-Z0-9, ]', '', text)

print("\n🧹 Cleaned Text:\n")
print(clean_text)

# Split ingredients by comma
ingredients = clean_text.split(",")

print("\n🍴 Ingredient List:\n")
for item in ingredients:
    item = item.strip()
    if item != "":
        print("-", item)

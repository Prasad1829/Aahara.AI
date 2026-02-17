import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import cv2
import pytesseract

# If tesseract not detected, set this path:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_with_ocr(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return ""

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Better OCR results
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    text = pytesseract.image_to_string(thresh)
    return text.strip()

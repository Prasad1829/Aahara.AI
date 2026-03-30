import cv2
import pytesseract
import re
import numpy as np

from app.config import TESSERACT_CMD

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def _extract_text_from_variants(image):
    # Multiple preprocessing variants improve OCR on packaging labels.
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    upscaled = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    adaptive = cv2.adaptiveThreshold(
        upscaled, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 8
    )
    otsu = cv2.threshold(upscaled, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    h, w = image.shape[:2]
    right_top_roi = image[0:int(h * 0.55), int(w * 0.40):w]
    roi_gray = cv2.cvtColor(right_top_roi, cv2.COLOR_BGR2GRAY)
    roi_upscaled = cv2.resize(roi_gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    roi_thresh = cv2.adaptiveThreshold(
        roi_upscaled, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 6
    )

    config = "--oem 3 --psm 6"
    roi_config = "--oem 3 --psm 4"

    texts = [
        pytesseract.image_to_string(adaptive, config=config),
        pytesseract.image_to_string(otsu, config=config),
        pytesseract.image_to_string(roi_thresh, config=roi_config),
    ]

    return "\n".join([t for t in texts if t and t.strip()])


def _extract_ingredients_from_text(text):
    if not text:
        return []

    normalized = re.sub(r"\s+", " ", text).strip()

    # Try to capture ingredient line after keyword.
    match = re.search(
        r"ingredients?\s*[:\-]?\s*([a-zA-Z,\s]+)",
        normalized,
        flags=re.IGNORECASE,
    )
    candidate = match.group(1) if match else normalized

    cleaned = re.sub(r"[^a-zA-Z, ]", "", candidate)
    items = [item.strip().lower() for item in cleaned.split(",") if item.strip()]

    # Remove common nutrition-table words from OCR noise.
    noise_words = {
        "energy", "protein", "fat", "sugar", "carbohydrates", "fiber", "serving",
        "size", "kcal", "total", "saturated", "mufa", "pufa", "packaged", "marketed",
    }
    items = [i for i in items if i not in noise_words and len(i) > 2]

    # Deduplicate while preserving order.
    deduped = list(dict.fromkeys(items))
    return deduped


def extract_text(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return []

    text = _extract_text_from_variants(image)
    ingredients = _extract_ingredients_from_text(text)
    return ingredients

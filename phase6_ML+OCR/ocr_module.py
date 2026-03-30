import os
import cv2
import pytesseract
import numpy as np

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ── Preprocessing ─────────────────────────────────────────────────────────────

def preprocess_image(img: np.ndarray) -> np.ndarray:
    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray  = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    blur  = cv2.GaussianBlur(gray, (0, 0), 3)
    sharp = cv2.addWeighted(gray, 1.5, blur, -0.5, 0)
    thresh = cv2.adaptiveThreshold(
        sharp, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 10
    )
    return thresh


# ── OCR confidence check ──────────────────────────────────────────────────────

OCR_MIN_CHARS = 10

def _has_meaningful_text(text: str) -> bool:
    cleaned = text.strip().replace("\n", "").replace(" ", "")
    return len(cleaned) >= OCR_MIN_CHARS


# ── Extract text ──────────────────────────────────────────────────────────────

def extract_text_with_ocr(image_path: str) -> dict:
    if not os.path.exists(image_path):
        return {
            "status": "error",
            "text": "",
            "is_text_image": False,
            "message": f"File not found: {image_path}"
        }

    img = cv2.imread(image_path)
    if img is None:
        return {
            "status": "error",
            "text": "",
            "is_text_image": False,
            "message": f"Could not read image: {image_path}"
        }

    processed = preprocess_image(img)
    config    = r"--oem 3 --psm 6"
    text      = pytesseract.image_to_string(processed, config=config).strip()

    has_text  = _has_meaningful_text(text)

    return {
        "status": "success",
        "text": text,
        "is_text_image": has_text,
        "message": "Text extracted successfully" if has_text else "No meaningful text found"
    }


# ── Ingredient parser ─────────────────────────────────────────────────────────

def extract_ingredients_from_text(raw_text: str) -> list:
    stop_words = {
        "the", "and", "with", "for", "from", "this", "that",
        "ingredients", "recipe", "contains", "made", "per",
        "serving", "amount", "total", "daily", "value",
    }

    words = raw_text.lower().replace(",", " ").replace(";", " ").split()
    ingredients = []

    for word in words:
        word = word.strip(".:()-*•/\\")
        if len(word) < 3:
            continue
        if word in stop_words:
            continue
        if word.replace(".", "").replace("%", "").isnumeric():
            continue
        if word not in ingredients:
            ingredients.append(word)

    return ingredients
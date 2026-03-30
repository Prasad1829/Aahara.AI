import os
import sys

import cv2
import numpy as np
import pytesseract


# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ── Preprocessing ─────────────────────────────────────────────────────────────

def preprocess_image(img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    blurred = cv2.GaussianBlur(gray, (0, 0), 3)
    sharp = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)
    thresh = cv2.adaptiveThreshold(
        sharp, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 10,
    )
    return thresh


# ── Core OCR ──────────────────────────────────────────────────────────────────

def _run_ocr(processed_img: np.ndarray) -> str:
    config = r"--oem 3 --psm 6"
    text = pytesseract.image_to_string(processed_img, config=config)
    return text.strip()


# ── From file path ────────────────────────────────────────────────────────────

def extract_text_from_path(image_path: str) -> dict:
    if not os.path.exists(image_path):
        return {"status": "error", "text": "", "message": f"File not found: {image_path}"}

    img = cv2.imread(image_path)
    if img is None:
        return {"status": "error", "text": "", "message": f"Could not read image: {image_path}"}

    processed = preprocess_image(img)
    text = _run_ocr(processed)
    return {"status": "success", "text": text, "message": "OCR completed successfully"}


# ── From uploaded bytes ───────────────────────────────────────────────────────

def extract_text_from_bytes(image_bytes: bytes) -> dict:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return {"status": "error", "text": "", "message": "Could not decode image bytes."}

    processed = preprocess_image(img)
    text = _run_ocr(processed)
    return {"status": "success", "text": text, "message": "OCR completed successfully"}


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


# ── Standalone CLI test ───────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:   python ocr_service.py <image_path>")
        print("Example: python ocr_service.py input/label.jpg")
        sys.exit(1)

    path = sys.argv[1]
    print(f"\nProcessing: {path}")
    print("-" * 40)

    result = extract_text_from_path(path)
    print(f"Status  : {result['status']}")
    print(f"Message : {result['message']}")
    print(f"\nExtracted Text:\n{result['text']}")

    if result["status"] == "success" and result["text"]:
        ingredients = extract_ingredients_from_text(result["text"])
        print(f"\nPossible Ingredients Found:")
        for item in ingredients:
            print(f"  - {item}")
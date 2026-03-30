import os
import sys

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from ocr_module import extract_text_with_ocr, extract_ingredients_from_text
from ml_module  import predict_ingredient


# ── Smart Combiner ────────────────────────────────────────────────────────────

def process_image(image_path: str) -> dict:
    """
    Smart routing:
      1. Run OCR first — if meaningful text found → OCR route
      2. Else run CNN  — if confidence >= 95%     → ML route
      3. Else          → not recognized
    """

    if not os.path.exists(image_path):
        return {
            "status": "error",
            "route": None,
            "result": None,
            "message": f"File not found: {image_path}"
        }

    # ── Step 1: Try OCR ───────────────────────────────────────────────────────
    ocr_result = extract_text_with_ocr(image_path)

    if ocr_result["status"] == "success" and ocr_result["is_text_image"]:
        ingredients = extract_ingredients_from_text(ocr_result["text"])
        return {
            "status": "success",
            "route": "OCR",
            "result": {
                "text": ocr_result["text"],
                "ingredients": ingredients
            },
            "message": "Text image detected — OCR used"
        }

    # ── Step 2: Try CNN ───────────────────────────────────────────────────────
    ml_result = predict_ingredient(image_path)

    if ml_result["status"] == "success":
        return {
            "status": "success",
            "route": "ML",
            "result": {
                "ingredient": ml_result["ingredient"],
                "confidence": ml_result["confidence"]
            },
            "message": f"Vegetable detected — ML used ({ml_result['confidence']}% confidence)"
        }

    # ── Step 3: Not recognized ────────────────────────────────────────────────
    return {
        "status": "not_recognized",
        "route": None,
        "result": None,
        "message": "Image not recognized — not a vegetable or text image"
    }


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:   python main.py <image_path>")
        print("Example: python main.py input/tomato.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    print(f"\nProcessing: {image_path}")
    print("-" * 40)

    result = process_image(image_path)

    print(f"Status  : {result['status']}")
    print(f"Route   : {result['route']}")
    print(f"Message : {result['message']}")
    print(f"Result  : {result['result']}")

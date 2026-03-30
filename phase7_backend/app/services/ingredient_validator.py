CONFIDENCE_THRESHOLD = 0.95
CONFIDENCE_MARGIN_THRESHOLD = 0.10

from app.services.indian_ingredients import INDIAN_INGREDIENT_CLASSES, normalize_ingredient

# ── Non-food keywords to reject immediately ───────────────────────────────────
NON_FOOD_KEYWORDS = [
    "bike", "motorcycle", "car", "vehicle", "person", "face", "human",
    "building", "road", "tree", "sky", "dog", "cat", "animal", "phone",
    "laptop", "computer", "chair", "table", "furniture", "clothes", "shirt",
    "signature", "handwriting", "logo", "brand"
]


def validate_detection(ml_result: dict, ocr_words: list, ocr_raw_text: str = "") -> dict:

    ml_confidence   = ml_result.get("confidence", 0)
    ml_ingredient   = normalize_ingredient(ml_result.get("ingredient", ""))
    top_predictions = ml_result.get("top_predictions", [])

    # ── Confidence margin ─────────────────────────────────────────────────────
    confidence_margin = 0.0
    if len(top_predictions) >= 2:
        confidence_margin = (
            float(top_predictions[0].get("confidence", 0))
            - float(top_predictions[1].get("confidence", 0))
        )

    # ── Normalize OCR words ───────────────────────────────────────────────────
    cleaned_ocr = [normalize_ingredient(word) for word in ocr_words]

    # ── Check ML validity ─────────────────────────────────────────────────────
    ml_valid = (
        ml_confidence >= CONFIDENCE_THRESHOLD and
        confidence_margin >= CONFIDENCE_MARGIN_THRESHOLD and
        ml_ingredient in INDIAN_INGREDIENT_CLASSES
    )

    # ── Extract valid OCR ingredients ─────────────────────────────────────────
    ocr_valid_ingredients = [
        word for word in cleaned_ocr if word in INDIAN_INGREDIENT_CLASSES
    ]

    # ── Check if OCR has meaningful text ──────────────────────────────────────
    has_text = bool(ocr_raw_text and len(ocr_raw_text.strip()) >= 5)

    # ── RULE 1: Both food ingredient AND text found ───────────────────────────
    if ml_valid and has_text:
        return {
            "status": "success",
            "source": "ml+ocr",
            "ingredients": [ml_ingredient],
            "confidence": ml_confidence,
            "text_found": ocr_raw_text.strip(),
            "message": f"Detected ingredient: {ml_ingredient} and text in image"
        }

    # ── RULE 2: Food ingredient found (no text) ───────────────────────────────
    if ml_valid:
        return {
            "status": "success",
            "source": "ml",
            "ingredients": [ml_ingredient],
            "confidence": ml_confidence,
            "text_found": None,
            "message": f"Detected ingredient: {ml_ingredient}"
        }

    # ── RULE 3: OCR found food ingredients ───────────────────────────────────
    if ocr_valid_ingredients and has_text:
        return {
            "status": "success",
            "source": "ocr",
            "ingredients": list(set(ocr_valid_ingredients)),
            "confidence": ml_confidence,
            "text_found": ocr_raw_text.strip(),
            "message": f"Detected ingredients from text: {', '.join(ocr_valid_ingredients)}"
        }

    if ocr_valid_ingredients:
        return {
            "status": "success",
            "source": "ocr",
            "ingredients": list(set(ocr_valid_ingredients)),
            "confidence": ml_confidence,
            "text_found": None,
            "message": f"Detected ingredients from text: {', '.join(ocr_valid_ingredients)}"
        }

    # ── RULE 4: Only text found (no food) ────────────────────────────────────
    if has_text and not ml_valid and not ocr_valid_ingredients:
        return {
            "status": "text_only",
            "source": "ocr",
            "ingredients": [],
            "confidence": ml_confidence,
            "text_found": ocr_raw_text.strip(),
            "message": f"Text found in image: {ocr_raw_text.strip()[:100]}"
        }

    # ── RULE 5: Non-food image (bike, person, etc.) ───────────────────────────
    # Low confidence across all predictions = not a food image
    all_low_confidence = all(
        float(p.get("confidence", 0)) < 0.5
        for p in top_predictions
    )

    if all_low_confidence or ml_confidence < 0.5:
        return {
            "status": "not_food",
            "source": "none",
            "ingredients": [],
            "confidence": ml_confidence,
            "text_found": None,
            "message": "❌ Not a food ingredient. Please upload a vegetable or food image."
        }

    # ── RULE 6: Food-like but not confident enough ────────────────────────────
    return {
        "status": "not_recognized",
        "source": "none",
        "ingredients": [],
        "confidence": ml_confidence,
        "text_found": None,
        "top_predictions": top_predictions,
        "message": "❌ Not a food ingredient. Please upload a vegetable or food image."
    }
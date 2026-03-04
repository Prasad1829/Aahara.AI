from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.auth import get_current_user
from app.models import User

import os
import shutil

from app.services.ingredient_validator import validate_detection
from app.services.ml_service import predict_ingredient
from app.services.ocr_services import extract_text
from app.services.recommendation_service import find_matching_recipes
from app.services.text_cleaner import clean_ocr_text

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        ml_result = predict_ingredient(file_path)

        raw_ocr_text = extract_text(file_path)

        # Fix: convert list to string if needed
        if isinstance(raw_ocr_text, list):
            raw_ocr_text = " ".join(raw_ocr_text)
        if not isinstance(raw_ocr_text, str):
            raw_ocr_text = str(raw_ocr_text) if raw_ocr_text else ""

        ocr_words = clean_ocr_text(raw_ocr_text)

        decision = validate_detection(ml_result, ocr_words, raw_ocr_text)

        detected_ingredients = [i.lower().strip() for i in decision.get("ingredients", [])]
        recommended_recipes = find_matching_recipes(detected_ingredients)

        return {
            "user": current_user.email,
            "detection": {
                "status": decision.get("status"),
                "source": decision.get("source"),
                "confidence": decision.get("confidence"),
                "top_predictions": ml_result.get("top_predictions", []),
                "text_found": decision.get("text_found"),
                "message": decision.get("message"),
            },
            "detected_ingredients": detected_ingredients,
            "recommended_recipes": recommended_recipes,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-recommendation")
def test_recommendation(current_user: User = Depends(get_current_user)):
    detected_ingredients = ["chicken", "onion", "tomato"]
    recommended = find_matching_recipes(detected_ingredients)
    return {
        "user": current_user.email,
        "detected_ingredients": detected_ingredients,
        "recommended_recipes": recommended,
    }


@router.get("/recommend")
def recommend_from_ingredients(
    ingredients: str,
    current_user: User = Depends(get_current_user),
):
    detected_ingredients = [item.strip().lower() for item in ingredients.split(",") if item.strip()]
    recommended = find_matching_recipes(detected_ingredients)
    return {
        "user": current_user.email,
        "detected_ingredients": detected_ingredients,
        "recommended_recipes": recommended,
    }
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Query

from app.auth import get_current_user
from app.models import User, Ingredient
from app.database import get_db
from sqlalchemy.orm import Session

import os
import shutil

from app.services.ml_service import predict_ingredient
from app.services.ocr_services import extract_text
from app.services.recommendation_service import get_recipe_recommendations
from app.services.text_cleaner import clean_ocr_text
from app.services.indian_ingredients import INDIAN_INGREDIENT_CLASSES, normalize_ingredient

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ML_CONFIDENCE_MIN = 0.30


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    preference: str | None = Query(default=None, pattern="^(veg|nonveg)?$"),
):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        ml_result = predict_ingredient(file_path)
        ml_confidence = float(ml_result.get("confidence", 0) or 0)
        ml_ingredient_raw = ml_result.get("ingredient", "")
        ml_ingredient = normalize_ingredient(ml_ingredient_raw)
        ml_ingredients = []
        if ml_ingredient and ml_ingredient in INDIAN_INGREDIENT_CLASSES and ml_confidence >= ML_CONFIDENCE_MIN:
            ml_ingredients = [ml_ingredient]

        ocr_raw = extract_text(file_path)
        if isinstance(ocr_raw, list):
            ocr_candidates = ocr_raw
        else:
            ocr_candidates = clean_ocr_text(ocr_raw)

        ocr_ingredients = []
        for word in ocr_candidates:
            normalized = normalize_ingredient(word)
            if normalized in INDIAN_INGREDIENT_CLASSES:
                ocr_ingredients.append(normalized)

        combined = []
        source = "none"
        if ml_ingredients and ocr_ingredients:
            combined = sorted(set(ml_ingredients + ocr_ingredients))
            source = "ml+ocr"
        elif ml_ingredients:
            combined = sorted(set(ml_ingredients))
            source = "ml"
        elif ocr_ingredients:
            combined = sorted(set(ocr_ingredients))
            source = "ocr"

        status = "success" if combined else "not_found"
        text_found = ", ".join(ocr_ingredients) if ocr_ingredients else None

        detected_ingredients = combined
        recommendation_data = get_recipe_recommendations(detected_ingredients, preference=preference)

        return {
            "user": current_user.email,
            "detection": {
                "status": status,
                "source": source,
                "confidence": ml_confidence,
                "top_predictions": ml_result.get("top_predictions", []),
                "text_found": text_found,
                "message": "Detected ingredients from image" if combined else "No ingredients detected",
            },
            "detected_ingredients": detected_ingredients,
            "recommended_recipes": recommendation_data["recommended_recipes"],
            "additional_recipes": recommendation_data["additional_recipes"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-recommendation")
def test_recommendation(current_user: User = Depends(get_current_user)):
    detected_ingredients = ["chicken", "onion", "tomato"]
    recommendation_data = get_recipe_recommendations(detected_ingredients)
    return {
        "user": current_user.email,
        "detected_ingredients": detected_ingredients,
        "recommended_recipes": recommendation_data["recommended_recipes"],
        "additional_recipes": recommendation_data["additional_recipes"],
    }


@router.get("/recommend")
def recommend_from_ingredients(
    ingredients: str,
    current_user: User = Depends(get_current_user),
    preference: str | None = Query(default=None, pattern="^(veg|nonveg)?$"),
):
    detected_ingredients = [item.strip().lower() for item in ingredients.split(",") if item.strip()]
    recommendation_data = get_recipe_recommendations(detected_ingredients, preference=preference)
    return {
        "user": current_user.email,
        "detected_ingredients": detected_ingredients,
        "recommended_recipes": recommendation_data["recommended_recipes"],
        "additional_recipes": recommendation_data["additional_recipes"],
    }


@router.post("/recommend")
def recommend_from_payload(
    payload: dict,
    current_user: User = Depends(get_current_user),
    preference: str | None = Query(default=None, pattern="^(veg|nonveg)?$"),
):
    ingredients = payload.get("ingredients", []) if isinstance(payload, dict) else []
    if not isinstance(ingredients, list):
        ingredients = []

    detected_ingredients = [item.strip().lower() for item in ingredients if isinstance(item, str) and item.strip()]
    recommendation_data = get_recipe_recommendations(detected_ingredients, preference=preference)
    return {
        "user": current_user.email,
        "detected_ingredients": detected_ingredients,
        "recommended_recipes": recommendation_data["recommended_recipes"],
        "additional_recipes": recommendation_data["additional_recipes"],
    }


@router.post("/recommend-recipes")
def recommend_recipes(
    payload: dict,
    current_user: User = Depends(get_current_user),
    preference: str | None = Query(default=None, pattern="^(veg|nonveg)?$"),
    db: Session = Depends(get_db),
):
    ingredients = payload.get("ingredients", []) if isinstance(payload, dict) else []
    if not isinstance(ingredients, list):
        ingredients = []

    normalized_inputs = []
    for item in ingredients:
        if item is None:
            continue
        text = str(item)
        parts = [p.strip() for p in text.split(",") if p.strip()]
        for part in parts:
            normalized_inputs.append(normalize_ingredient(part))

    normalized_inputs = [i for i in normalized_inputs if i]

    valid_set = {row[0] for row in db.query(Ingredient.name).all()}
    if normalized_inputs and not any(i in valid_set for i in normalized_inputs):
        return {
            "user": current_user.email,
            "recipes": [],
            "message": "Check your ingredient spelling.",
        }

    recommendation_data = get_recipe_recommendations(normalized_inputs, preference=preference)
    return {
        "user": current_user.email,
        "recommended_recipes": recommendation_data["recommended_recipes"],
        "additional_recipes": recommendation_data["additional_recipes"],
        "recipes": recommendation_data["recommended_recipes"],
        "message": "No recipes found for the selected ingredients."
        if not recommendation_data["recommended_recipes"] and not recommendation_data["additional_recipes"]
        else None,
    }

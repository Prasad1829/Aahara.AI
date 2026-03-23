from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Query

from app.auth import get_current_user
from app.models import User, Ingredient
from app.database import get_db
from sqlalchemy.orm import Session

import os
import re
import uuid
import base64
import shutil
import requests

from PIL import Image as PILImage

from app.services.ml_service import predict_ingredient
from app.services.ocr_services import extract_text
from app.services.recommendation_service import get_recipe_recommendations
from app.services.text_cleaner import clean_ocr_text
from app.services.indian_ingredients import INDIAN_INGREDIENT_CLASSES, normalize_ingredient

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ML_CONFIDENCE_MIN = 0.50  # increased for better accuracy

ALLOWED_EXTENSIONS = {
    'jpg', 'jpeg', 'png', 'webp', 'avif',
    'bmp', 'tiff', 'tif', 'heic', 'heif'
}


def convert_to_jpg(input_path: str) -> str:
    try:
        img = PILImage.open(input_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        jpg_path = input_path.rsplit('.', 1)[0] + '_converted.jpg'
        img.save(jpg_path, 'JPEG', quality=95)
        if input_path != jpg_path:
            try:
                os.remove(input_path)
            except Exception:
                pass
        return jpg_path
    except Exception as e:
        print(f"[Image Convert] Failed: {e}")
        return input_path


def is_food_related(name: str) -> bool:
    FOOD_KEYWORDS = {
        'apple', 'banana', 'mango', 'tomato', 'potato', 'onion', 'garlic',
        'ginger', 'chili', 'pepper', 'lemon', 'lime', 'orange', 'grape',
        'rice', 'wheat', 'flour', 'sugar', 'salt', 'oil', 'butter', 'ghee',
        'chicken', 'mutton', 'beef', 'pork', 'fish', 'prawn', 'egg',
        'milk', 'cream', 'yogurt', 'paneer', 'cheese', 'tofu',
        'spinach', 'cabbage', 'carrot', 'broccoli', 'cauliflower', 'peas',
        'lentil', 'dal', 'bean', 'chickpea', 'mushroom', 'cucumber',
        'eggplant', 'brinjal', 'coriander', 'mint', 'turmeric', 'cumin',
        'cardamom', 'cinnamon', 'clove', 'bay', 'mustard', 'fennel',
        'bread', 'roti', 'chapati', 'naan', 'pasta', 'noodle',
        'coconut', 'almond', 'cashew', 'peanut', 'walnut',
    }
    return any(kw in name for kw in FOOD_KEYWORDS)


def extract_ingredients_from_ocr_text(raw_text: str) -> list:
    if not raw_text:
        return []
    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
    results = []
    for i, line in enumerate(lines):
        if re.match(r'^ingredients?\s*:', line, re.IGNORECASE):
            section_lines = lines[i:i+5]
            match = re.search(r'ingredients?\s*:\s*(.+)', ' '.join(section_lines), re.IGNORECASE)
            if match:
                for part in re.split(r'[,;]', match.group(1)):
                    part = re.sub(r'\([^)]*\)', '', part).strip().lower()
                    part = re.sub(r'\d+\.?\d*\s*%', '', part).strip()
                    part = re.sub(r'[^a-z\s\-]', '', part).strip()
                    if 3 <= len(part) <= 40:
                        results.append(part)
                if results:
                    return results[:10]
    SKIP = [r'^\d+\s*g', r'^\d+\s*ml', r'^rs\.?\s*\d+', r'^mrp',
            r'^best before', r'^mfg\.', r'^batch', r'^fssai',
            r'^manufactured by', r'^marketed by']
    for line in lines:
        ll = line.lower()
        if any(re.match(p, ll) for p in SKIP):
            continue
        if len(line) < 3 or len(line) > 60:
            continue
        if sum(c.isalpha() for c in line) / max(len(line), 1) < 0.4:
            continue
        best = re.sub(r'[^a-z\s\-]', '', ll).strip()
        if best and len(best) > 2:
            return [best]
    return []


# ── Google Cloud Vision API ──
# ALWAYS runs — multiple ingredients detect cheyyadaniki
def run_vision_api(image_path: str) -> list:
    api_key = os.getenv("GOOGLE_CLOUD_VISION_API_KEY", "")
    if not api_key:
        print("[Vision API] No API key in .env — skipping")
        return []
    try:
        with open(image_path, 'rb') as f:
            image_b64 = base64.b64encode(f.read()).decode('utf-8')

        response = requests.post(
            f'https://vision.googleapis.com/v1/images:annotate?key={api_key}',
            json={'requests': [{'image': {'content': image_b64}, 'features': [
                {'type': 'TEXT_DETECTION', 'maxResults': 1},
                {'type': 'LABEL_DETECTION', 'maxResults': 20},
                {'type': 'OBJECT_LOCALIZATION', 'maxResults': 15},
            ]}]},
            timeout=15,
        )
        if response.status_code != 200:
            print(f"[Vision API] HTTP {response.status_code}")
            return []

        result = response.json().get('responses', [{}])[0]

        # OCR
        raw_text = ''
        if result.get('fullTextAnnotation'):
            raw_text = result['fullTextAnnotation'].get('text', '').strip()
        elif result.get('textAnnotations'):
            raw_text = result['textAnnotations'][0].get('description', '').strip()
        text_ings = extract_ingredients_from_ocr_text(raw_text) if raw_text else []

        STOP = {
            'food', 'ingredient', 'product', 'brand', 'label', 'packaging',
            'design', 'art', 'text', 'font', 'logo', 'yellow', 'red', 'blue',
            'green', 'white', 'still life', 'close-up', 'photography', 'image',
            'natural foods', 'whole food', 'superfood', 'vegetarian food',
            'produce', 'local food', 'staple food', 'dish', 'cuisine',
        }

        # Label detection
        label_ings = [
            lbl['description'].lower()
            for lbl in result.get('labelAnnotations', [])
            if lbl.get('score', 0) > 0.70
            and lbl['description'].lower() not in STOP
            and len(lbl['description']) > 2
        ]

        # Object localization — most reliable for multiple objects
        obj_ings = [
            obj.get('name', '').lower()
            for obj in result.get('localizedObjectAnnotations', [])
            if obj.get('score', 0) > 0.60
            and is_food_related(obj.get('name', '').lower())
            and obj.get('name', '').lower() not in STOP
        ]

        # Combine — objects first (most accurate), then labels, then text
        seen = set()
        combined = []
        for ing in obj_ings + text_ings + label_ings:
            if ing and ing not in seen and is_food_related(ing):
                seen.add(ing)
                combined.append(ing)

        print(f"[Vision API] Raw detected: {combined}")
        return combined

    except Exception as e:
        print(f"[Vision API] Error: {e}")
        return []


# ══════════════════════════════════════════
#  /upload
# ══════════════════════════════════════════
@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    preference: str | None = Query(default=None, pattern="^(veg|nonveg)?$"),
):
    try:
        # ── 1. Validate extension ──
        filename = (file.filename or "image.jpg").lower()
        extension = filename.rsplit('.', 1)[-1] if '.' in filename else 'jpg'
        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: .{extension}. Use JPG, PNG, WebP, AVIF, BMP or TIFF"
            )

        # ── 2. Read + size check ──
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image too large. Max 10MB allowed.")

        # ── 3. Save ──
        unique_name = f"{uuid.uuid4().hex}.{extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        with open(file_path, 'wb') as f:
            f.write(content)

        # ── 4. Convert to JPG ──
        if extension not in {'jpg', 'jpeg'}:
            file_path = convert_to_jpg(file_path)

        # ── 5. Verify readable ──
        try:
            img_check = PILImage.open(file_path)
            img_check.verify()
        except Exception:
            try:
                pil_img = PILImage.open(file_path).convert('RGB')
                fixed_path = file_path.rsplit('.', 1)[0] + '_fixed.jpg'
                pil_img.save(fixed_path, 'JPEG', quality=95)
                file_path = fixed_path
            except Exception:
                try:
                    os.remove(file_path)
                except Exception:
                    pass
                raise HTTPException(
                    status_code=400,
                    detail="Could not read this image. Please try a different one."
                )

        # ══ STEP A: ML Model ══
        ml_ingredients = []
        ml_confidence = 0.0
        ml_result = {}
        try:
            ml_result = predict_ingredient(file_path)
            ml_confidence = float(ml_result.get("confidence", 0) or 0)
            ml_ingredient = normalize_ingredient(ml_result.get("ingredient", ""))
            if ml_ingredient and ml_ingredient in INDIAN_INGREDIENT_CLASSES and ml_confidence >= ML_CONFIDENCE_MIN:
                ml_ingredients = [ml_ingredient]
                print(f"[ML] Detected: {ml_ingredient} ({ml_confidence:.2f})")
            else:
                print(f"[ML] Low confidence or not in classes: {ml_ingredient} ({ml_confidence:.2f})")
        except Exception as e:
            print(f"[ML] Error: {e}")

        # ══ STEP B: OCR ══
        ocr_ingredients = []
        text_found = None
        try:
            ocr_raw = extract_text(file_path)
            ocr_candidates = ocr_raw if isinstance(ocr_raw, list) else clean_ocr_text(ocr_raw)
            for word in ocr_candidates:
                norm = normalize_ingredient(word)
                if norm in INDIAN_INGREDIENT_CLASSES:
                    ocr_ingredients.append(norm)
            text_found = ", ".join(ocr_ingredients) if ocr_ingredients else None
        except Exception as e:
            print(f"[OCR] Error: {e}")

        # ══ STEP C: Combine ML + OCR ══
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

        # ══ STEP D: Vision API — ALWAYS runs for multiple ingredient detection ══
        vision_ings = run_vision_api(file_path)
        if vision_ings:
            normalized_vision = []
            for ing in vision_ings:
                norm = normalize_ingredient(ing)
                # Only INDIAN_INGREDIENT_CLASSES match chestha — random labels avoid chestam
                if norm and norm in INDIAN_INGREDIENT_CLASSES and norm not in combined:
                    normalized_vision.append(norm)
            if normalized_vision:
                combined = list(dict.fromkeys(combined + normalized_vision))
                source = (source + "+vision_api") if source != "none" else "vision_api"
                print(f"[Vision API] Added new: {normalized_vision}")

        # ── Cleanup ──
        try:
            os.remove(file_path)
        except Exception:
            pass

        # ══ STEP E: Recommendations ══
        status_str = "success" if combined else "not_found"
        recommendation_data = get_recipe_recommendations(combined, preference=preference)

        print(f"[Final] Ingredients: {combined} | Source: {source}")

        return {
            "user": current_user.email,
            "detection": {
                "status": status_str,
                "source": source,
                "confidence": ml_confidence,
                "top_predictions": ml_result.get("top_predictions", []),
                "text_found": text_found,
                "message": "Detected ingredients from image" if combined else "No ingredients detected",
            },
            "detected_ingredients": combined,
            "recommended_recipes": recommendation_data["recommended_recipes"],
            "additional_recipes": recommendation_data["additional_recipes"],
        }

    except HTTPException:
        raise
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
        for part in str(item).split(","):
            part = part.strip()
            if part:
                normalized_inputs.append(normalize_ingredient(part))
    normalized_inputs = [i for i in normalized_inputs if i]
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

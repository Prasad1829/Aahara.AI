import csv
import os

from app.database import SessionLocal
from app.models import Ingredient, Recipe
from app.services.indian_ingredients import INDIAN_INGREDIENT_CLASSES, normalize_ingredient


DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "indian_food.csv")
TARGET_STATES = {"andhra pradesh", "telangana"}

PANTRY_INGREDIENTS = [
    "salt",
    "oil",
    "chili powder",
    "turmeric",
    "black pepper",
    "cumin",
    "coriander powder",
    "garam masala",
]


def _split_ingredients(raw_value: str) -> list[str]:
    if not raw_value:
        return []
    parts = [p.strip() for p in raw_value.split(",")]
    return [p for p in parts if p]


def _normalize_ingredients(items: list[str]) -> list[str]:
    normalized = []
    for item in items:
        value = normalize_ingredient(item)
        if value:
            normalized.append(value)
    return normalized


def import_regional_recipes():
    csv_path = os.path.abspath(DATA_PATH)
    if not os.path.exists(csv_path):
        return {"status": "skipped", "reason": f"CSV not found: {csv_path}"}

    db = SessionLocal()
    try:
        ingredient_cache = {}
        imported = 0
        skipped = 0

        with open(csv_path, "r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                state = (row.get("state") or "").strip().lower()
                if state not in TARGET_STATES:
                    continue

                name = (row.get("name") or "").strip()
                if not name:
                    continue

                existing = db.query(Recipe).filter(Recipe.name == name).first()
                if existing is not None:
                    skipped += 1
                    continue

                ingredients_raw = _split_ingredients(row.get("ingredients", ""))
                ingredients = _normalize_ingredients(ingredients_raw)

                pantry_items = _normalize_ingredients(PANTRY_INGREDIENTS)
                all_ingredients = sorted({*ingredients, *pantry_items})

                recipe = Recipe(name=name)
                diet = (row.get("diet") or "").strip().lower()
                if diet:
                    recipe.is_veg = diet in {"vegetarian", "veg"}
                db.add(recipe)
                db.flush()

                for ing_name in all_ingredients:
                    if not ing_name:
                        continue
                    ingredient = ingredient_cache.get(ing_name)
                    if ingredient is None:
                        ingredient = db.query(Ingredient).filter(Ingredient.name == ing_name).first()
                        if ingredient is None:
                            ingredient = Ingredient(name=ing_name)
                            db.add(ingredient)
                            db.flush()
                        ingredient_cache[ing_name] = ingredient
                    recipe.ingredients.append(ingredient)

                imported += 1

        db.commit()
        return {"status": "ok", "imported": imported, "skipped": skipped}
    finally:
        db.close()

from app.database import SessionLocal
from app.models import Recipe
from app.services.indian_ingredients import normalize_ingredient
from app.services.image_service import FALLBACK_IMAGE_URL, get_cached_recipe_image_url


OPTIONAL_INGREDIENTS = {
    "oil",
    "salt",
    "water",
    "turmeric",
    "cumin",
    "cumin powder",
    "coriander powder",
    "garam masala",
    "chili",
    "chili powder",
    "green chili",
    "black pepper",
    "mustard seeds",
    "curry leaves",
    "cinnamon",
    "cloves",
    "cardamom",
    "bay leaf",
    "hing",
    "asafoetida",
    "coriander",
    "mint",
}

BASE_INGREDIENTS = {
    "onion",
    "tomato",
    "garlic",
    "ginger",
    "ginger garlic paste",
}


def _build_recipe_payload(recipe, matched, missing, match_score, db):
    instructions = [s.strip() for s in (recipe.instructions or "").split("\n") if s.strip()]
    ingredients = sorted({normalize_ingredient(ing.name) for ing in recipe.ingredients if normalize_ingredient(ing.name)})
    return {
        "name": recipe.name,
        "is_veg": recipe.is_veg,
        "cooking_time_minutes": recipe.cooking_time_minutes,
        "image_url": get_cached_recipe_image_url(recipe, db),
        "image_fallback_url": FALLBACK_IMAGE_URL,
        "ingredients": ingredients,
        "match_score": round(match_score, 2),
        "matched_ingredients": sorted(list(matched)),
        "missing_ingredients": sorted(list(missing)),
        "instructions": instructions,
    }


def _normalize_detected_ingredients(detected_ingredients) -> set[str]:
    detected_set = set()
    for item in detected_ingredients:
        if not item:
            continue
        if isinstance(item, str):
            parts = [p.strip() for p in item.split(",") if p.strip()]
        else:
            parts = [str(item).strip()]
        for part in parts:
            normalized = normalize_ingredient(part)
            if normalized:
                detected_set.add(normalized)
    return detected_set


def get_recipe_recommendations(detected_ingredients, preference: str | None = None):
    db = SessionLocal()
    try:
        detected_set = _normalize_detected_ingredients(detected_ingredients)
        if not detected_set:
            return {
                "recommended_recipes": [],
                "additional_recipes": [],
            }

        recipes_query = db.query(Recipe)
        if preference == "veg":
            recipes_query = recipes_query.filter(Recipe.is_veg.is_(True))
        elif preference == "nonveg":
            recipes_query = recipes_query.filter(Recipe.is_veg.is_(False))
        recipes = recipes_query.all()

        minimum_match_ratio = 0.6
        recommended_results = []
        additional_results = []

        for recipe in recipes:
            recipe_ingredients = [normalize_ingredient(ing.name) for ing in recipe.ingredients]
            recipe_set = {ingredient for ingredient in recipe_ingredients if ingredient}
            if not recipe_set:
                continue

            significant_ingredients = recipe_set - OPTIONAL_INGREDIENTS
            if not significant_ingredients:
                significant_ingredients = set(recipe_set)

            matched = detected_set.intersection(significant_ingredients)
            if not matched:
                continue

            missing = significant_ingredients - detected_set
            match_score = len(matched) / len(significant_ingredients)

            primary_ingredients = significant_ingredients - BASE_INGREDIENTS
            if not primary_ingredients:
                primary_ingredients = set(significant_ingredients)

            matched_primary = detected_set.intersection(primary_ingredients)
            missing_primary = primary_ingredients - detected_set
            primary_match_ratio = len(matched_primary) / len(primary_ingredients) if primary_ingredients else 0
            has_primary_match = bool(matched_primary)

            payload = _build_recipe_payload(recipe, matched, missing, match_score, db)

            if primary_match_ratio >= minimum_match_ratio and has_primary_match:
                recommended_results.append(payload)
            else:
                additional_results.append(payload)

        sort_key = lambda item: (item["match_score"], len(item["matched_ingredients"]), -len(item["missing_ingredients"]))
        recommended_results.sort(key=sort_key, reverse=True)
        additional_results.sort(key=sort_key, reverse=True)

        return {
            "recommended_recipes": recommended_results,
            "additional_recipes": additional_results,
        }
    finally:
        db.close()


def find_matching_recipes(detected_ingredients, preference: str | None = None):
    return get_recipe_recommendations(detected_ingredients, preference=preference)["recommended_recipes"]

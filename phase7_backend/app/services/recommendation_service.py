from app.database import SessionLocal
from app.models import Recipe
from app.services.indian_ingredients import normalize_ingredient
from app.services.image_service import get_recipe_image_url, FALLBACK_IMAGE_URL


def _build_recipe_payload(recipe, matched, missing, match_score):
    instructions = [s.strip() for s in (recipe.instructions or "").split("\n") if s.strip()]
    return {
        "name": recipe.name,
        "is_veg": recipe.is_veg,
        "cooking_time_minutes": recipe.cooking_time_minutes,
        "image_url": get_recipe_image_url(recipe.name),
        "image_fallback_url": FALLBACK_IMAGE_URL,
        "match_score": round(match_score, 2),
        "matched_ingredients": sorted(list(matched)),
        "missing_ingredients": sorted(list(missing)),
        "instructions": instructions,
    }


def find_matching_recipes(detected_ingredients, preference: str | None = None):
    db = SessionLocal()
    try:
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
        recipes_query = db.query(Recipe)
        if preference == "veg":
            recipes_query = recipes_query.filter(Recipe.is_veg.is_(True))
        elif preference == "nonveg":
            recipes_query = recipes_query.filter(Recipe.is_veg.is_(False))
        recipes = recipes_query.all()

        strong_results = []
        weak_results = []

        for recipe in recipes:
            recipe_ingredients = [normalize_ingredient(ing.name) for ing in recipe.ingredients]
            recipe_set = set(recipe_ingredients)
            if not recipe_set:
                continue

            matched = detected_set.intersection(recipe_set)
            if not matched:
                continue

            missing = recipe_set - detected_set
            match_score = len(matched) / len(recipe_set)
            payload = _build_recipe_payload(recipe, matched, missing, match_score)

            if match_score >= 0.3:
                strong_results.append(payload)
            else:
                weak_results.append(payload)

        strong_results.sort(key=lambda x: x["match_score"], reverse=True)
        weak_results.sort(key=lambda x: x["match_score"], reverse=True)

        if strong_results:
            return strong_results[:5]

        # Fallback: still return suggestions if at least one ingredient matched.
        return weak_results[:5]
    finally:
        db.close()

from app.database import SessionLocal
from app.models import Recipe
from app.services.indian_ingredients import normalize_ingredient


def _build_recipe_payload(recipe, matched, missing, match_score):
    instructions = [s.strip() for s in (recipe.instructions or "").split("\n") if s.strip()]
    return {
        "name": recipe.name,
        "is_veg": recipe.is_veg,
        "cooking_time_minutes": recipe.cooking_time_minutes,
        "match_score": round(match_score, 2),
        "matched_ingredients": sorted(list(matched)),
        "missing_ingredients": sorted(list(missing)),
        "instructions": instructions,
    }


def find_matching_recipes(detected_ingredients):
    db = SessionLocal()
    try:
        detected_set = {
            normalize_ingredient(i) for i in detected_ingredients if i and i.strip()
        }
        recipes = db.query(Recipe).all()

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

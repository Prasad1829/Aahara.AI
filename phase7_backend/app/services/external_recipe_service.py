import os

import requests

from app.services.image_service import FALLBACK_IMAGE_URL
from app.services.indian_ingredients import normalize_ingredient


REQUEST_TIMEOUT_SECONDS = 4
SPOONACULAR_URL = "https://api.spoonacular.com/recipes/findByIngredients"
MEALDB_FILTER_URL = "https://www.themealdb.com/api/json/v1/1/filter.php"
MEALDB_LOOKUP_URL = "https://www.themealdb.com/api/json/v1/1/lookup.php"
NON_VEG_INGREDIENTS = {"chicken", "mutton", "fish", "prawns", "egg", "beef", "pork", "lamb", "meat"}
SOUTH_INDIAN_KEYWORDS = {
    "south indian",
    "andhra",
    "telangana",
    "tamil",
    "tamil nadu",
    "kerala",
    "karnataka",
    "chettinad",
    "udupi",
    "dosa",
    "masala dosa",
    "idli",
    "vada",
    "sambar",
    "rasam",
    "upma",
    "pongal",
    "uttapam",
    "uthappam",
    "appam",
    "puttu",
    "paniyaram",
    "poriyal",
    "kootu",
    "kuzhambu",
    "pachadi",
    "sadam",
    "thoran",
    "avial",
    "curry leaves",
    "coconut oil",
    "coconut milk",
    "sambar powder",
    "rasam powder",
    "tamarind",
    "drumstick",
}


def _normalize_detected_set(detected_ingredients) -> set[str]:
    detected_set = set()
    for item in detected_ingredients or []:
        if item is None:
            continue
        parts = str(item).split(",")
        for part in parts:
            normalized = normalize_ingredient(part.strip())
            if normalized:
                detected_set.add(normalized)
    return detected_set


def _build_external_payload(
    name: str,
    matched: set[str],
    missing: set[str],
    match_score: float,
    *,
    image_url: str | None = None,
    is_veg=None,
    cooking_time_minutes=None,
    ingredients: list[str] | None = None,
):
    return {
        "name": name,
        "is_veg": is_veg,
        "cooking_time_minutes": cooking_time_minutes,
        "image_url": image_url or FALLBACK_IMAGE_URL,
        "image_fallback_url": FALLBACK_IMAGE_URL,
        "ingredients": ingredients or sorted(list(matched | missing)),
        "match_score": round(match_score, 2),
        "matched_ingredients": sorted(list(matched)),
        "missing_ingredients": sorted(list(missing)),
    }


def _matches_preference(payload: dict, preference: str | None) -> bool:
    if preference not in {"veg", "nonveg"}:
        return True

    ingredients = {normalize_ingredient(item) for item in payload.get("ingredients", [])}
    text = f"{payload.get('name', '')} {' '.join(sorted(ingredients))}".lower()
    inferred_nonveg = any(keyword in text for keyword in NON_VEG_INGREDIENTS)

    if preference == "veg":
        return not inferred_nonveg
    return inferred_nonveg


def _matches_south_indian_style(payload: dict) -> bool:
    ingredients = {normalize_ingredient(item) for item in payload.get("ingredients", [])}
    text = f"{payload.get('name', '')} {' '.join(sorted(ingredients))}".lower()
    return any(keyword in text for keyword in SOUTH_INDIAN_KEYWORDS)


def _get_json(url: str, params: dict[str, str]):
    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def _fetch_spoonacular_recipes(detected_set: set[str], limit: int) -> dict[str, list[dict]]:
    api_key = os.getenv("SPOONACULAR_API_KEY", "").strip()
    if not api_key or not detected_set:
        return {"recommended_recipes": [], "additional_recipes": []}

    data = _get_json(
        SPOONACULAR_URL,
        {
            "apiKey": api_key,
            "ingredients": ",".join(sorted(detected_set)),
            "number": str(limit),
            "ranking": "2",
            "ignorePantry": "true",
        },
    )

    if not isinstance(data, list):
        return {"recommended_recipes": [], "additional_recipes": []}

    recommended = []
    additional = []

    for item in data:
        used = {
            normalize_ingredient((ingredient or {}).get("name", ""))
            for ingredient in item.get("usedIngredients", [])
        }
        missed = {
            normalize_ingredient((ingredient or {}).get("name", ""))
            for ingredient in item.get("missedIngredients", [])
        }
        used.discard("")
        missed.discard("")

        if not used:
            continue

        total = len(used) + len(missed)
        match_score = len(used) / total if total else 0
        payload = _build_external_payload(
            item.get("title", "Recipe"),
            used,
            missed,
            match_score,
            image_url=item.get("image"),
            ingredients=sorted(list(used | missed)),
        )
        if not _matches_south_indian_style(payload):
            continue

        if match_score >= 0.6 or len(used) >= 2:
            recommended.append(payload)
        else:
            additional.append(payload)

    return {
        "recommended_recipes": recommended,
        "additional_recipes": additional,
    }


def _extract_meal_ingredients(meal: dict) -> set[str]:
    ingredients = set()
    for index in range(1, 21):
        ingredient = normalize_ingredient((meal.get(f"strIngredient{index}") or "").strip())
        if ingredient:
            ingredients.add(ingredient)
    return ingredients


def _fetch_mealdb_recipes(detected_set: set[str], limit: int) -> dict[str, list[dict]]:
    if not detected_set:
        return {"recommended_recipes": [], "additional_recipes": []}

    meal_hits: dict[str, dict] = {}

    for ingredient in sorted(detected_set):
        data = _get_json(MEALDB_FILTER_URL, {"i": ingredient})
        for meal in data.get("meals") or []:
            meal_id = str(meal.get("idMeal") or "").strip()
            if not meal_id:
                continue
            entry = meal_hits.setdefault(
                meal_id,
                {
                    "id": meal_id,
                    "name": meal.get("strMeal") or "Recipe",
                    "image_url": meal.get("strMealThumb"),
                    "matched": set(),
                },
            )
            entry["matched"].add(ingredient)

    ranked_meal_ids = sorted(
        meal_hits,
        key=lambda meal_id: (
            len(meal_hits[meal_id]["matched"]),
            meal_hits[meal_id]["name"],
        ),
        reverse=True,
    )[:limit]

    recommended = []
    additional = []

    for meal_id in ranked_meal_ids:
        detail_data = _get_json(MEALDB_LOOKUP_URL, {"i": meal_id})
        meals = detail_data.get("meals") or []
        if not meals:
            continue

        meal = meals[0]
        recipe_ingredients = _extract_meal_ingredients(meal)
        matched = detected_set.intersection(recipe_ingredients) or set(meal_hits[meal_id]["matched"])
        missing = recipe_ingredients - detected_set
        total = len(recipe_ingredients) if recipe_ingredients else len(matched)
        match_score = len(matched) / total if total else 0

        payload = _build_external_payload(
            meal.get("strMeal") or meal_hits[meal_id]["name"],
            matched,
            missing,
            match_score,
            image_url=meal.get("strMealThumb") or meal_hits[meal_id]["image_url"],
            ingredients=sorted(list(recipe_ingredients)) if recipe_ingredients else None,
        )
        if not _matches_south_indian_style(payload):
            continue

        if match_score >= 0.5 or len(matched) >= 2:
            recommended.append(payload)
        else:
            additional.append(payload)

    return {
        "recommended_recipes": recommended,
        "additional_recipes": additional,
    }


def get_external_recipe_recommendations(
    detected_ingredients,
    preference: str | None = None,
    limit: int = 6,
) -> dict[str, list[dict]]:
    detected_set = _normalize_detected_set(detected_ingredients)
    if not detected_set:
        return {"recommended_recipes": [], "additional_recipes": []}

    try:
        spoonacular_results = _fetch_spoonacular_recipes(detected_set, limit)
        spoonacular_results["recommended_recipes"] = [
            recipe for recipe in spoonacular_results["recommended_recipes"] if _matches_preference(recipe, preference)
        ]
        spoonacular_results["additional_recipes"] = [
            recipe for recipe in spoonacular_results["additional_recipes"] if _matches_preference(recipe, preference)
        ]
        if spoonacular_results["recommended_recipes"] or spoonacular_results["additional_recipes"]:
            return spoonacular_results
    except requests.RequestException:
        pass
    except ValueError:
        pass

    try:
        mealdb_results = _fetch_mealdb_recipes(detected_set, limit)
        mealdb_results["recommended_recipes"] = [
            recipe for recipe in mealdb_results["recommended_recipes"] if _matches_preference(recipe, preference)
        ]
        mealdb_results["additional_recipes"] = [
            recipe for recipe in mealdb_results["additional_recipes"] if _matches_preference(recipe, preference)
        ]
        return mealdb_results
    except requests.RequestException:
        return {"recommended_recipes": [], "additional_recipes": []}
    except ValueError:
        return {"recommended_recipes": [], "additional_recipes": []}

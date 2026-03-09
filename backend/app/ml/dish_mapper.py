import json
import os
from functools import lru_cache

from app.ml.ingredient_normalizer import normalize_ingredient, normalize_ingredients_list


DEFAULT_MAPPING_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "config", "dish_to_ingredients.json")
)

FALLBACK_STOPWORDS = {"and", "with", "style", "soup", "salad", "sandwich", "cake"}


def _normalize_dish_key(dish_name):
    return str(dish_name or "").strip().lower().replace(" ", "_")


@lru_cache(maxsize=1)
def _load_mapping():
    if not os.path.exists(DEFAULT_MAPPING_PATH):
        return {}
    try:
        with open(DEFAULT_MAPPING_PATH, "r", encoding="utf-8") as file_obj:
            data = json.load(file_obj) or {}
        if not isinstance(data, dict):
            return {}

        normalized = {}
        for key, values in data.items():
            dish_key = _normalize_dish_key(key)
            items = normalize_ingredients_list(values if isinstance(values, list) else [])
            if items:
                normalized[dish_key] = items
        return normalized
    except Exception:
        return {}


class DishIngredientMapper:
    def __init__(self):
        self.mapping = _load_mapping()

    def dish_to_ingredients(self, dish_name, max_items=6):
        key = _normalize_dish_key(dish_name)
        ingredients = list(self.mapping.get(key, []))

        if not ingredients:
            fallback = []
            for token in key.split("_"):
                normalized = normalize_ingredient(token)
                if not normalized or normalized in FALLBACK_STOPWORDS:
                    continue
                fallback.append(normalized)
            ingredients = normalize_ingredients_list(fallback)

        if max_items and max_items > 0:
            return ingredients[: int(max_items)]
        return ingredients

    def predictions_to_ingredients(self, predictions, min_confidence=0.0):
        rows = []
        for prediction in predictions or []:
            dish = prediction.get("ingredient")
            try:
                confidence = float(prediction.get("confidence", 0.0))
            except Exception:
                confidence = 0.0

            if confidence < float(min_confidence):
                continue

            ingredients = self.dish_to_ingredients(dish, max_items=8)
            source = "image" if confidence >= 0.3 else "model_guess"
            if not ingredients:
                continue

            for ingredient in ingredients:
                rows.append(
                    {
                        "ingredient": ingredient,
                        "confidence": round(confidence, 4),
                        "source": source,
                        "dish": dish,
                    }
                )
        return rows


_mapper = None


def get_dish_mapper():
    global _mapper
    if _mapper is None:
        _mapper = DishIngredientMapper()
    return _mapper

from collections import defaultdict
from functools import lru_cache
from threading import Lock

from app.ml.ingredient_normalizer import normalize_ingredient
from app.services.recipe_service import get_recipe_service


class IngredientSuggester:
    _instance = None
    _instance_lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._cooccur = {}
        self._ingredient_frequency = {}
        self._build_stats()
        self._initialized = True

    def _build_stats(self):
        recipe_service = get_recipe_service()
        recipes = recipe_service.get_all_recipes() or []

        cooccur = defaultdict(lambda: defaultdict(int))
        frequency = defaultdict(int)

        for recipe in recipes:
            ingredients = recipe.get("normalized_ingredients") or []
            unique_ingredients = []
            seen = set()
            for ingredient in ingredients:
                token = normalize_ingredient(ingredient)
                if not token or token in seen:
                    continue
                seen.add(token)
                unique_ingredients.append(token)

            for ingredient in unique_ingredients:
                frequency[ingredient] += 1

            for i, source in enumerate(unique_ingredients):
                for j, target in enumerate(unique_ingredients):
                    if i == j:
                        continue
                    cooccur[source][target] += 1

        self._cooccur = {src: dict(targets) for src, targets in cooccur.items()}
        self._ingredient_frequency = dict(frequency)

    @lru_cache(maxsize=512)
    def suggest(self, ingredient, limit=10):
        token = normalize_ingredient(ingredient)
        if not token:
            return []

        neighbors = self._cooccur.get(token, {})
        if not neighbors:
            return []

        base_count = max(int(self._ingredient_frequency.get(token, 1)), 1)
        rows = []
        for candidate, count in neighbors.items():
            candidate_freq = max(int(self._ingredient_frequency.get(candidate, 1)), 1)
            confidence = float(count) / float(base_count)
            lift = (float(count) * 1000.0) / float(base_count * candidate_freq)
            score = (confidence * 0.7) + (min(lift, 5.0) * 0.3)
            rows.append(
                {
                    "ingredient": candidate,
                    "count": int(count),
                    "confidence": round(confidence, 4),
                    "score": round(score, 4),
                }
            )

        rows.sort(key=lambda item: (item["score"], item["count"]), reverse=True)
        return rows[: max(1, int(limit))]


ingredient_suggester = IngredientSuggester()


def get_ingredient_suggester():
    return ingredient_suggester

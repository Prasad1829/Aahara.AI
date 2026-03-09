import json
import os
from statistics import mean

from evaluation.metrics import precision_recall, recall_at_k, top_k_hit

from app.ml.ingredient_normalizer import normalize_ingredients_list
from app.services.recipe_service import get_recipe_service


class SystemEvaluator:
    def __init__(self, benchmark_path=None, max_cases=200):
        self.recipe_service = get_recipe_service()
        self.max_cases = max(10, int(max_cases))
        default_path = os.path.join(os.path.dirname(__file__), "data", "benchmark_cases.json")
        self.benchmark_path = benchmark_path or default_path

    def _load_cases_from_file(self):
        if not os.path.exists(self.benchmark_path):
            return []
        try:
            with open(self.benchmark_path, "r", encoding="utf-8") as file_obj:
                rows = json.load(file_obj) or []
            if not isinstance(rows, list):
                return []
            cases = []
            for row in rows:
                if not isinstance(row, dict):
                    continue
                query = normalize_ingredients_list(row.get("query_ingredients") or [])
                expected_ingredients = normalize_ingredients_list(row.get("expected_ingredients") or [])
                expected_recipe_ids = []
                for item in row.get("expected_recipe_ids") or []:
                    try:
                        expected_recipe_ids.append(int(item))
                    except Exception:
                        continue
                if not query:
                    continue
                if not expected_recipe_ids:
                    continue
                cases.append(
                    {
                        "query_ingredients": query,
                        "expected_ingredients": expected_ingredients or query,
                        "expected_recipe_ids": expected_recipe_ids,
                    }
                )
            return cases
        except Exception:
            return []

    def _build_synthetic_cases(self):
        cases = []
        for recipe in self.recipe_service.get_all_recipes():
            ingredients = normalize_ingredients_list(recipe.get("normalized_ingredients") or [])
            if len(ingredients) < 2:
                continue
            query = ingredients[: min(3, len(ingredients))]
            expected = ingredients[: min(5, len(ingredients))]
            cases.append(
                {
                    "query_ingredients": query,
                    "expected_ingredients": expected,
                    "expected_recipe_ids": [int(recipe.get("id"))],
                }
            )
            if len(cases) >= self.max_cases:
                break
        return cases

    def _load_cases(self):
        cases = self._load_cases_from_file()
        if cases:
            return cases[: self.max_cases]
        return self._build_synthetic_cases()

    def run(self):
        cases = self._load_cases()
        if not cases:
            return {
                "num_cases": 0,
                "ingredient_detection_precision": 0.0,
                "ingredient_detection_recall": 0.0,
                "top5_recipe_accuracy": 0.0,
                "top10_recipe_accuracy": 0.0,
                "recall_at_5": 0.0,
                "recall_at_10": 0.0,
                "benchmark_source": self.benchmark_path,
            }

        precision_scores = []
        recall_scores = []
        top5_scores = []
        top10_scores = []
        recall5_scores = []
        recall10_scores = []

        for case in cases:
            query_ingredients = normalize_ingredients_list(case.get("query_ingredients") or [])
            expected_ingredients = normalize_ingredients_list(case.get("expected_ingredients") or [])
            expected_recipe_ids = [int(rid) for rid in (case.get("expected_recipe_ids") or []) if str(rid).isdigit()]

            precision, recall = precision_recall(query_ingredients, expected_ingredients or query_ingredients)
            precision_scores.append(precision)
            recall_scores.append(recall)

            term_weights = {term: 5.0 for term in query_ingredients}
            recommendations = self.recipe_service.recommend_recipes(
                query_terms=query_ingredients,
                limit=10,
                term_weights=term_weights,
                use_semantic=False,
            )
            predicted_ids = []
            for recipe in recommendations:
                try:
                    predicted_ids.append(int(recipe.get("id")))
                except Exception:
                    continue

            top5_scores.append(top_k_hit(predicted_ids, expected_recipe_ids, 5))
            top10_scores.append(top_k_hit(predicted_ids, expected_recipe_ids, 10))
            recall5_scores.append(recall_at_k(predicted_ids, expected_recipe_ids, 5))
            recall10_scores.append(recall_at_k(predicted_ids, expected_recipe_ids, 10))

        return {
            "num_cases": len(cases),
            "ingredient_detection_precision": round(mean(precision_scores), 4),
            "ingredient_detection_recall": round(mean(recall_scores), 4),
            "top5_recipe_accuracy": round(mean(top5_scores), 4),
            "top10_recipe_accuracy": round(mean(top10_scores), 4),
            "recall_at_5": round(mean(recall5_scores), 4),
            "recall_at_10": round(mean(recall10_scores), 4),
            "benchmark_source": self.benchmark_path if os.path.exists(self.benchmark_path) else "synthetic_from_dataset",
        }


import ast
import difflib
import json
import logging
import os
import re
import time
from functools import lru_cache
from threading import Lock

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.ml.dish_mapper import get_dish_mapper
from app.ml.recipe_dataset_loader import get_recipe_dataset_loader
from app.ml.ingredient_normalizer import (
    extract_base_ingredient,
    normalize_ingredient,
    normalize_ingredients_list,
)
from app.services.recipe_image_service import get_recipe_image_service
from app.utils.system_metrics import record_metric


logger = logging.getLogger(__name__)

NON_VEG_INGREDIENT_MARKERS = {
    "chicken",
    "mutton",
    "fish",
    "egg",
    "shrimp",
    "pork",
    "beef",
    "bacon",
    "turkey",
}

NON_VEG_MARKER_PATTERNS = {
    marker: re.compile(rf"\b{re.escape(marker)}\b", flags=re.IGNORECASE)
    for marker in NON_VEG_INGREDIENT_MARKERS
}

COOKING_METHOD_MINUTES = {
    "bake": 18,
    "roast": 22,
    "grill": 16,
    "fry": 14,
    "deep fry": 16,
    "boil": 10,
    "simmer": 15,
    "pressure cook": 18,
    "slow cook": 40,
    "steam": 10,
    "saute": 8,
}

LOW_QUALITY_PATTERNS = (
    "combine the vegetables in a pot",
    "mix everything",
    "cook and serve",
)

SIMILARITY_MATCH_THRESHOLD = 0.62
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class RecipeService:
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

        self._recipes = []
        self._recipe_by_id = {}
        self._search_documents = []

        self._tfidf_vectorizer = None
        self._tfidf_matrix = None

        self._embedding_model = None
        self._recipe_embeddings = None
        self._embedding_enabled = True
        self._embedding_dim = 0
        self._faiss_index = None
        self._faiss_enabled = True

        self._short_text_embedding_cache = {}
        self._image_service = get_recipe_image_service()

        self._load_and_prepare_recipes()
        self._build_tfidf_index()
        self._build_or_load_vector_assets()
        self._initialized = True
        print(f"[OK] Recipe service initialized with {len(self._recipes)} recipes")

    @staticmethod
    def _normalize_text(value):
        text = str(value or "").lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _tokenize_words(value):
        return [
            token
            for token in re.split(r"[^a-z0-9]+", str(value or "").lower())
            if token
        ]

    @staticmethod
    def _parse_list_like(value):
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]

        text = str(value).strip()
        if not text:
            return []

        for parser in (json.loads, ast.literal_eval):
            try:
                parsed = parser(text)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except Exception:
                pass

        return [item.strip() for item in re.split(r",|\n|;", text) if item.strip()]

    @staticmethod
    def _base_dir():
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))

    @classmethod
    def _workspace_dir(cls):
        return os.path.abspath(os.path.join(cls._base_dir(), ".."))

    @staticmethod
    def _dedupe_paths(paths):
        unique = []
        seen = set()
        for path in paths:
            clean = os.path.abspath(path)
            if clean in seen:
                continue
            seen.add(clean)
            unique.append(clean)
        return unique

    @classmethod
    def _dataset_roots(cls):
        base_dir = cls._base_dir()
        workspace_dir = cls._workspace_dir()
        env_roots = [
            str(os.getenv("DATASET_ROOT", "")).strip(),
            str(os.getenv("RECIPE_DATASET_ROOT", "")).strip(),
        ]
        roots = []
        for value in env_roots:
            if value:
                roots.append(os.path.abspath(os.path.expanduser(value)))
        roots.extend(
            [
                os.path.join(workspace_dir, "dataset"),
                os.path.join(base_dir, "dataset"),
                os.path.join(base_dir, "backend", "dataset"),
            ]
        )
        return cls._dedupe_paths(roots)

    @classmethod
    def _recipe_paths(cls):
        relative_files = [
            ("processed", "recipes", "recipes_normalized.json"),
            ("processed", "recipes", "indian_recipes_normalized.json"),
            ("processed", "recipes", "recipes_custom.json"),
            ("recipes", "test.json"),
        ]
        merge_roots = str(os.getenv("RECIPE_MERGE_DATASET_ROOTS", "0")).strip() != "0"
        explicit_root = (
            str(os.getenv("DATASET_ROOT", "")).strip()
            or str(os.getenv("RECIPE_DATASET_ROOT", "")).strip()
        )
        if explicit_root and not merge_roots:
            roots = [os.path.abspath(os.path.expanduser(explicit_root))]
        else:
            roots = cls._dataset_roots()
        paths = []
        for root in roots:
            root_hits = []
            for rel_parts in relative_files:
                candidate = os.path.join(root, *rel_parts)
                if os.path.exists(candidate):
                    root_hits.append(candidate)
            if root_hits:
                paths.extend(root_hits)
                if not merge_roots:
                    break
        return cls._dedupe_paths(paths)

    @classmethod
    def _dataset_asset_path(cls, filename):
        explicit_root = (
            str(os.getenv("DATASET_ROOT", "")).strip()
            or str(os.getenv("RECIPE_DATASET_ROOT", "")).strip()
        )
        if explicit_root:
            target_root = os.path.abspath(os.path.expanduser(explicit_root))
            os.makedirs(target_root, exist_ok=True)
            return os.path.join(target_root, filename)

        roots = cls._dataset_roots()
        for root in roots:
            candidate = os.path.join(root, filename)
            if os.path.exists(candidate):
                return candidate
        target_root = roots[0] if roots else os.path.join(cls._base_dir(), "dataset")
        os.makedirs(target_root, exist_ok=True)
        return os.path.join(target_root, filename)

    @classmethod
    def _vector_asset_suffix(cls):
        primary = (
            str(os.getenv("RECIPE_PRIMARY_DATASET_PATH", "")).strip()
            or str(os.getenv("RECIPE1M_DATASET_PATH", "")).strip()
        )
        if not primary:
            return "default"
        dataset_name = os.path.splitext(os.path.basename(primary))[0].lower()
        dataset_name = re.sub(r"[^a-z0-9]+", "_", dataset_name).strip("_") or "primary"
        max_rows = str(os.getenv("RECIPE_DATASET_MAX_ROWS", "")).strip() or "all"
        return f"{dataset_name}_{max_rows}"

    @classmethod
    def _embeddings_path(cls):
        suffix = cls._vector_asset_suffix()
        return cls._dataset_asset_path(f"recipe_embeddings_{suffix}.npy")

    @classmethod
    def _faiss_index_path(cls):
        suffix = cls._vector_asset_suffix()
        return cls._dataset_asset_path(f"faiss_recipe_index_{suffix}.bin")

    def _read_recipe_sources(self):
        merged = []
        primary_rows = get_recipe_dataset_loader().load_primary_recipes()
        if primary_rows:
            merged.extend(primary_rows)
            print(f"[OK] Loaded primary recipe dataset (Recipe1M-style): {len(primary_rows)} rows")

        paths = self._recipe_paths()
        if not paths:
            print("[!] No default recipe JSON sources found in dataset roots")

        for path in paths:
            if not os.path.exists(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as file_obj:
                    rows = json.load(file_obj) or []
                if not isinstance(rows, list):
                    continue
                merged.extend(rows)
                print(f"[OK] Loaded recipes dataset: {path} ({len(rows)} rows)")
            except Exception as exc:
                print(f"[!] Failed to load recipes from {path}: {exc}")
        return merged

    @staticmethod
    def _parse_minutes_from_text(value):
        text = str(value or "").lower()
        if not text:
            return 0
        total = 0
        for count, _unit in re.findall(r"(\d+)\s*(h|hr|hrs|hour|hours)", text):
            total += int(count) * 60
        for count, _unit in re.findall(r"(\d+)\s*(m|min|mins|minute|minutes)", text):
            total += int(count)
        if total > 0:
            return total
        number_match = re.search(r"\b(\d{1,3})\b", text)
        if number_match:
            return int(number_match.group(1))
        return 0

    def _normalize_instructions(self, value):
        rows = self._parse_list_like(value)
        if not rows and isinstance(value, str):
            rows = [
                step.strip()
                for step in re.split(r"[.\n]+", value)
                if str(step).strip()
            ]

        steps = []
        for row in rows:
            clean = re.sub(r"\s+", " ", str(row or "").strip())
            clean = clean.strip(" -")
            if len(clean) < 8:
                continue
            steps.append(clean)

        if not steps:
            return ["No detailed instructions available."]

        return steps[:30]

    def _estimate_cooking_time_minutes(self, recipe):
        explicit = self._parse_minutes_from_text(recipe.get("cook_time")) + self._parse_minutes_from_text(
            recipe.get("prep_time")
        )
        if explicit > 0:
            return int(max(10, min(240, explicit)))

        name = self._normalize_text(recipe.get("name"))
        ingredients = recipe.get("normalized_ingredients") or []
        instructions = recipe.get("instructions") or []
        instruction_text = " ".join(str(step).lower() for step in instructions)
        combined = f"{name} {instruction_text}"

        ingredient_count = max(len(ingredients), 1)
        step_count = max(len(instructions), 1)

        method_bonus = 0
        for method, minutes in COOKING_METHOD_MINUTES.items():
            if method in combined:
                method_bonus += minutes

        complexity = (ingredient_count * 3.2) + (step_count * 4.5) + method_bonus
        estimated = int(round(max(12.0, min(180.0, complexity))))
        # round to nearest 5 minutes for cleaner UI
        return int(max(10, round(estimated / 5.0) * 5))

    def _compute_quality_score(self, recipe):
        ingredients = recipe.get("normalized_ingredients") or []
        instructions = recipe.get("instructions") or []
        ingredient_score = min(len(ingredients) / 10.0, 1.0)
        step_score = min(len(instructions) / 8.0, 1.0)

        avg_step_words = 0.0
        if instructions:
            avg_step_words = sum(len(self._tokenize_words(step)) for step in instructions) / float(len(instructions))
        detail_score = min(avg_step_words / 14.0, 1.0)

        text_blob = " ".join(str(step).lower() for step in instructions)
        penalty = 0.0
        for pattern in LOW_QUALITY_PATTERNS:
            if pattern in text_blob:
                penalty += 0.08

        score = (ingredient_score * 0.45) + (step_score * 0.35) + (detail_score * 0.20) - penalty
        return float(max(0.0, min(1.0, score)))

    def _classify_recipe_type(self, normalized_ingredients):
        for ingredient in normalized_ingredients or []:
            ingredient_text = str(ingredient or "").strip().lower()
            if not ingredient_text:
                continue
            for marker, pattern in NON_VEG_MARKER_PATTERNS.items():
                if pattern.search(ingredient_text):
                    logger.debug("[classify] '%s' matched non-veg marker '%s'", ingredient_text, marker)
                    return "non-veg"
        return "veg"

    def _normalize_recipe_row(self, row):
        recipe = dict(row or {})

        try:
            recipe_id = int(recipe.get("id"))
        except Exception:
            return None

        name = str(recipe.get("name") or f"Recipe {recipe_id}").strip()
        ingredients_raw = self._parse_list_like(recipe.get("ingredients"))
        normalized_ingredients = []
        for ingredient in ingredients_raw:
            base = extract_base_ingredient(ingredient)
            normalized = normalize_ingredient(base)
            if normalized:
                normalized_ingredients.append(normalized)
        normalized_ingredients = normalize_ingredients_list(normalized_ingredients)

        recipe["id"] = recipe_id
        recipe["name"] = name
        recipe["recipe_name"] = name
        recipe["ingredients"] = ingredients_raw
        recipe["normalized_ingredients"] = normalized_ingredients
        recipe["instructions"] = self._normalize_instructions(recipe.get("instructions"))
        recipe["recipe_type"] = self._classify_recipe_type(normalized_ingredients)
        recipe["cooking_time_minutes"] = self._estimate_cooking_time_minutes(recipe)
        recipe["cooking_time"] = f"{recipe['cooking_time_minutes']} min"
        recipe["quality_score"] = self._compute_quality_score(recipe)

        image_url = str(recipe.get("image_url") or "").strip()
        recipe["image_url"] = image_url or None
        recipe["image_source"] = "dataset" if image_url else "fallback"

        return recipe

    def _dedupe_by_name(self, rows):
        unique = []
        seen = set()
        for recipe in rows:
            if not recipe:
                continue
            key = self._normalize_text(recipe.get("name")) or f"id-{recipe.get('id')}"
            if key in seen:
                continue
            seen.add(key)
            unique.append(recipe)
        return unique

    def _load_and_prepare_recipes(self):
        raw_rows = self._read_recipe_sources()
        normalized = []
        for row in raw_rows:
            prepared = self._normalize_recipe_row(row)
            if prepared:
                normalized.append(prepared)

        self._recipes = self._dedupe_by_name(normalized)
        self._recipe_by_id = {int(recipe["id"]): recipe for recipe in self._recipes}
        self._search_documents = [
            f"{self._normalize_text(recipe.get('name'))} {' '.join(recipe.get('normalized_ingredients') or [])}".strip()
            for recipe in self._recipes
        ]

    def _build_tfidf_index(self):
        if not self._search_documents:
            return
        try:
            self._tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
            self._tfidf_matrix = self._tfidf_vectorizer.fit_transform(self._search_documents)
            print("[OK] TF-IDF index built")
        except Exception as exc:
            self._tfidf_vectorizer = None
            self._tfidf_matrix = None
            print(f"[!] TF-IDF index build failed: {exc}")

    def _query_text_from_weights(self, weighted_terms):
        parts = []
        for term, weight in weighted_terms.items():
            repeats = max(1, int(round(float(weight))))
            parts.extend([term] * repeats)
        return " ".join(parts).strip()

    def _tfidf_candidates(self, weighted_terms, top_k=400):
        total_recipes = len(self._recipes)
        if total_recipes == 0:
            return [], {}

        if self._tfidf_vectorizer is None or self._tfidf_matrix is None:
            indexes = list(range(min(total_recipes, top_k)))
            return indexes, {idx: 0.0 for idx in indexes}

        query_text = self._query_text_from_weights(weighted_terms)
        if not query_text:
            indexes = list(range(min(total_recipes, top_k)))
            return indexes, {idx: 0.0 for idx in indexes}

        try:
            query_vector = self._tfidf_vectorizer.transform([query_text])
            similarities = cosine_similarity(query_vector, self._tfidf_matrix).ravel()
        except Exception:
            indexes = list(range(min(total_recipes, top_k)))
            return indexes, {idx: 0.0 for idx in indexes}

        top_k = min(max(int(top_k), 1), total_recipes)
        top_indexes = np.argpartition(similarities, -top_k)[-top_k:]
        sorted_indexes = top_indexes[np.argsort(similarities[top_indexes])[::-1]]
        score_map = {int(index): float(similarities[index]) for index in sorted_indexes}
        return [int(index) for index in sorted_indexes], score_map

    def _load_embedding_model(self):
        if self._embedding_model is not None:
            return True
        if not self._embedding_enabled:
            return False

        try:
            from sentence_transformers import SentenceTransformer

            local_only = str(os.getenv("EMBEDDING_LOCAL_FILES_ONLY", "0")).strip() != "0"
            model_source = self._resolve_embedding_model_source(local_only=local_only)
            self._embedding_model = SentenceTransformer(
                model_source,
                local_files_only=local_only,
            )
            return True
        except Exception as exc:
            self._embedding_enabled = False
            self._embedding_model = None
            print(f"[!] Sentence-transformers unavailable: {exc}")
            return False

    @classmethod
    def _resolve_embedding_model_source(cls, local_only):
        configured = (
            str(os.getenv("EMBEDDING_MODEL_NAME_OR_PATH", "")).strip()
            or str(os.getenv("EMBEDDING_MODEL_PATH", "")).strip()
        )
        if configured:
            return configured

        if local_only:
            for root in cls._dataset_roots():
                candidate = os.path.join(root, "hf_models", "all-MiniLM-L6-v2")
                if os.path.isdir(candidate):
                    return candidate

        return DEFAULT_EMBEDDING_MODEL

    def embedding_model_loaded(self):
        return self._embedding_model is not None

    def _encode_documents(self, docs):
        if not self._load_embedding_model():
            return None
        try:
            vectors = self._embedding_model.encode(
                docs,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
            return np.asarray(vectors, dtype=np.float32)
        except Exception as exc:
            self._embedding_enabled = False
            print(f"[!] Embedding generation failed: {exc}")
            return None

    def _build_or_load_embeddings(self):
        if not self._embedding_enabled:
            return

        path = self._embeddings_path()
        embeddings = None

        if os.path.exists(path):
            try:
                loaded = np.load(path)
                if (
                    isinstance(loaded, np.ndarray)
                    and loaded.ndim == 2
                    and loaded.shape[0] == len(self._recipes)
                    and loaded.shape[1] > 0
                ):
                    embeddings = loaded.astype(np.float32)
                    norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-12
                    embeddings = embeddings / norms
                    print(f"[OK] Loaded recipe embeddings from {path}")
            except Exception as exc:
                print(f"[!] Could not load embeddings cache: {exc}")

        if embeddings is None:
            embeddings = self._encode_documents(self._search_documents)
            if embeddings is None:
                return
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                np.save(path, embeddings)
                print(f"[OK] Saved recipe embeddings to {path}")
            except Exception as exc:
                print(f"[!] Could not save embeddings cache: {exc}")

        self._recipe_embeddings = embeddings
        self._embedding_dim = int(embeddings.shape[1])

    def _build_or_load_faiss(self):
        self._faiss_index = None
        if not self._faiss_enabled or self._recipe_embeddings is None:
            return

        try:
            import faiss
        except Exception as exc:
            self._faiss_enabled = False
            print(f"[!] FAISS unavailable: {exc}")
            return

        path = self._faiss_index_path()
        index = None
        if os.path.exists(path):
            try:
                loaded_index = faiss.read_index(path)
                if (
                    int(loaded_index.ntotal) == int(self._recipe_embeddings.shape[0])
                    and int(loaded_index.d) == int(self._recipe_embeddings.shape[1])
                ):
                    index = loaded_index
                    print(f"[OK] Loaded FAISS index from {path}")
            except Exception as exc:
                print(f"[!] Could not load FAISS index: {exc}")

        if index is None:
            try:
                index = faiss.IndexFlatIP(int(self._recipe_embeddings.shape[1]))
                index.add(np.asarray(self._recipe_embeddings, dtype=np.float32))
                os.makedirs(os.path.dirname(path), exist_ok=True)
                faiss.write_index(index, path)
                print(f"[OK] Built and saved FAISS index to {path}")
            except Exception as exc:
                self._faiss_enabled = False
                print(f"[!] Could not build FAISS index: {exc}")
                index = None

        self._faiss_index = index

    def _build_or_load_vector_assets(self):
        self._build_or_load_embeddings()
        self._build_or_load_faiss()

    def _vector_candidates(self, query_text, top_k=100):
        if not query_text:
            return [], {}
        if self._recipe_embeddings is None:
            return [], {}
        if not self._load_embedding_model():
            return [], {}

        try:
            query_vector = self._embedding_model.encode(
                [query_text],
                convert_to_numpy=True,
                normalize_embeddings=True,
            ).astype(np.float32)
        except Exception:
            return [], {}

        top_k = min(max(int(top_k), 1), len(self._recipes))

        if self._faiss_index is not None:
            try:
                faiss_started = time.perf_counter()
                scores, indices = self._faiss_index.search(query_vector, top_k)
                record_metric("faiss_search_time_ms", (time.perf_counter() - faiss_started) * 1000.0)
                rows = []
                score_map = {}
                for idx, score in zip(indices[0].tolist(), scores[0].tolist()):
                    if idx < 0:
                        continue
                    rows.append(int(idx))
                    score_map[int(idx)] = float(score)
                return rows, score_map
            except Exception:
                pass

        fallback_started = time.perf_counter()
        sims = np.dot(self._recipe_embeddings, query_vector[0])
        record_metric("faiss_search_time_ms", (time.perf_counter() - fallback_started) * 1000.0)
        top_indexes = np.argpartition(sims, -top_k)[-top_k:]
        sorted_indexes = top_indexes[np.argsort(sims[top_indexes])[::-1]]
        score_map = {int(index): float(sims[index]) for index in sorted_indexes}
        return [int(index) for index in sorted_indexes], score_map

    def _get_text_embedding(self, value):
        text = self._normalize_text(value)
        if not text:
            return None
        cached = self._short_text_embedding_cache.get(text)
        if cached is not None:
            return cached
        if not self._load_embedding_model():
            return None
        try:
            vector = self._embedding_model.encode(
                [text],
                convert_to_numpy=True,
                normalize_embeddings=True,
            ).astype(np.float32)[0]
            if len(self._short_text_embedding_cache) > 50000:
                self._short_text_embedding_cache.pop(next(iter(self._short_text_embedding_cache)))
            self._short_text_embedding_cache[text] = vector
            return vector
        except Exception:
            return None

    def _ingredient_similarity(self, query_term, ingredient):
        query = normalize_ingredient(query_term)
        target = normalize_ingredient(ingredient)
        if not query or not target:
            return 0.0
        if query == target:
            return 1.0

        query_tokens = set(self._tokenize_words(query))
        target_tokens = set(self._tokenize_words(target))

        # Prevent false positives like "egg" matching "eggplant".
        if query in NON_VEG_INGREDIENT_MARKERS and query not in target_tokens:
            return 0.0

        lexical_score = 0.0
        if query_tokens and target_tokens:
            overlap = len(query_tokens.intersection(target_tokens))
            if overlap > 0:
                union = len(query_tokens.union(target_tokens)) or 1
                lexical_score = max(lexical_score, overlap / float(union))
                if query_tokens.issubset(target_tokens) or target_tokens.issubset(query_tokens):
                    lexical_score = max(lexical_score, 0.88)

        lexical_score = max(lexical_score, difflib.SequenceMatcher(None, query, target).ratio() * 0.82)

        embedding_score = 0.0
        if len(query) > 2 and len(target) > 2:
            q_vector = self._get_text_embedding(query)
            t_vector = self._get_text_embedding(target)
            if q_vector is not None and t_vector is not None:
                embedding_score = float(np.dot(q_vector, t_vector))

        # Short query terms must keep a lexical anchor to avoid semantic overreach.
        if len(query) <= 4 and lexical_score < 0.5:
            return lexical_score

        return max(lexical_score, embedding_score)

    def _term_matches_ingredient(self, term, ingredient):
        return self._ingredient_similarity(term, ingredient) >= SIMILARITY_MATCH_THRESHOLD

    @staticmethod
    def _build_reason_text(coverage, missing_penalty, avg_similarity, quality_score):
        if coverage >= 0.70 and missing_penalty <= 0.28:
            return "High ingredient match and low missing ingredients"
        if avg_similarity >= 0.78 and quality_score >= 0.55:
            return "Strong semantic ingredient similarity with a high-quality recipe profile"
        if coverage >= 0.50:
            return "Good ingredient overlap with moderate recipe fit"
        return "Partial ingredient overlap; add missing ingredients for better results"

    def _score_recipe(self, recipe, weighted_terms, query_text):
        recipe_ingredients = recipe.get("normalized_ingredients") or []
        if not recipe_ingredients:
            return None

        recipe_ingredient_set = sorted(set(recipe_ingredients))
        query_terms = [term for term in weighted_terms.keys() if term]
        if not query_terms:
            return None

        matched_query_scores = {}
        matched_recipe_ingredients = {}
        for term in query_terms:
            best_similarity = 0.0
            best_ingredient = None
            for ingredient in recipe_ingredient_set:
                similarity = self._ingredient_similarity(term, ingredient)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_ingredient = ingredient
            matched_query_scores[term] = best_similarity
            if best_similarity >= SIMILARITY_MATCH_THRESHOLD and best_ingredient:
                matched_recipe_ingredients[best_ingredient] = max(
                    best_similarity,
                    matched_recipe_ingredients.get(best_ingredient, 0.0),
                )

        matched_terms = {term for term, score in matched_query_scores.items() if score >= SIMILARITY_MATCH_THRESHOLD}
        matched_recipe_list = sorted(matched_recipe_ingredients.keys())
        missing_recipe_ingredients = sorted(
            ingredient for ingredient in recipe_ingredient_set if ingredient not in matched_recipe_ingredients
        )

        total_recipe_ingredients = max(len(recipe_ingredient_set), 1)
        matched_recipe_count = len(matched_recipe_list)
        base_coverage = matched_recipe_count / total_recipe_ingredients

        total_query_weight = sum(float(weight) for weight in weighted_terms.values()) or 1.0
        matched_query_weight = 0.0
        weighted_similarity_sum = 0.0
        for term, weight in weighted_terms.items():
            similarity = float(matched_query_scores.get(term, 0.0))
            if similarity >= SIMILARITY_MATCH_THRESHOLD:
                matched_query_weight += float(weight)
            weighted_similarity_sum += float(weight) * similarity
        weighted_match_ratio = matched_query_weight / total_query_weight
        weighted_similarity_ratio = weighted_similarity_sum / total_query_weight

        ingredient_coverage = (base_coverage * 0.52) + (weighted_match_ratio * 0.23) + (weighted_similarity_ratio * 0.25)
        ingredient_coverage = max(0.0, min(1.0, ingredient_coverage))

        missing_penalty = (total_recipe_ingredients - matched_recipe_count) / float(total_recipe_ingredients)
        name_similarity = difflib.SequenceMatcher(
            None,
            self._normalize_text(query_text),
            self._normalize_text(recipe.get("name")),
        ).ratio()

        avg_similarity = 0.0
        if matched_terms:
            avg_similarity = sum(matched_query_scores.get(term, 0.0) for term in matched_terms) / float(len(matched_terms))

        quality_score = float(recipe.get("quality_score", 0.0))

        score = (
            (ingredient_coverage * 10.0)
            + (avg_similarity * 2.4)
            + (name_similarity * 2.2)
            + (quality_score * 1.4)
            - (missing_penalty * 4.0)
        )

        return {
            "ingredient_coverage": ingredient_coverage,
            "base_coverage": base_coverage,
            "missing_penalty": missing_penalty,
            "name_similarity": name_similarity,
            "avg_similarity": avg_similarity,
            "quality_score": quality_score,
            "score": score,
            "matched_recipe_ingredients": matched_recipe_list,
            "missing_recipe_ingredients": missing_recipe_ingredients,
        }

    def _prepare_weighted_terms(self, query_terms=None, term_weights=None):
        weights = {}

        for term in query_terms or []:
            normalized = normalize_ingredient(term)
            if not normalized:
                continue
            weights[normalized] = max(weights.get(normalized, 0.0), 1.0)

        for term, weight in (term_weights or {}).items():
            normalized = normalize_ingredient(term)
            if not normalized:
                continue
            try:
                numeric_weight = float(weight)
            except Exception:
                numeric_weight = 1.0
            weights[normalized] = max(weights.get(normalized, 0.0), numeric_weight)

        return {term: weight for term, weight in weights.items() if term}

    def _attach_image_url(self, recipe):
        explicit = str(recipe.get("image_url") or "").strip()
        if explicit:
            recipe["image_source"] = "dataset"
            return explicit

        image_url, source = self._image_service.get_image_for_recipe(
            recipe_name=recipe.get("name"),
            recipe_type=recipe.get("recipe_type"),
        )
        recipe["image_source"] = source
        return image_url

    def _enrich_recipe_for_response(self, recipe, explanation=None, score=None):
        row = dict(recipe or {})
        row["recipe_name"] = row.get("name") or row.get("recipe_name") or f"Recipe {row.get('id')}"
        row["recipe_type"] = row.get("recipe_type") or self._classify_recipe_type(row.get("normalized_ingredients") or [])
        row["cooking_time_minutes"] = int(row.get("cooking_time_minutes") or self._estimate_cooking_time_minutes(row))
        row["cooking_time"] = f"{row['cooking_time_minutes']} min"
        row["image_url"] = self._attach_image_url(row)

        if explanation:
            row["explanation"] = explanation
            row["matched_ingredients"] = list(explanation.get("matched") or [])
        else:
            row.setdefault("explanation", {})
            row.setdefault("matched_ingredients", [])

        if score is not None:
            row["match_score"] = round(float(score), 4)

        logger.info(
            "[recipe] %s | type=%s | score=%s | image=%s (%s)",
            row.get("recipe_name"),
            row.get("recipe_type"),
            row.get("match_score"),
            row.get("image_url"),
            row.get("image_source"),
        )
        return row

    @lru_cache(maxsize=512)
    def _recommend_recipes_cached(self, weighted_terms_key, limit, use_semantic):
        weighted_terms = {term: float(weight) for term, weight in weighted_terms_key}
        if not weighted_terms:
            return ()

        query_text = self._query_text_from_weights(weighted_terms)
        if not query_text:
            return ()

        vector_indexes, vector_scores = self._vector_candidates(query_text, top_k=100)
        candidate_indexes = list(vector_indexes)

        tfidf_indexes, tfidf_scores = self._tfidf_candidates(weighted_terms, top_k=max(int(limit) * 100, 450))
        for idx in tfidf_indexes:
            if idx not in candidate_indexes:
                candidate_indexes.append(idx)

        if not candidate_indexes:
            return ()

        ranking_started = time.perf_counter()
        scored_rows = []
        for index in candidate_indexes:
            if index < 0 or index >= len(self._recipes):
                continue
            recipe = self._recipes[index]
            metrics = self._score_recipe(recipe, weighted_terms, query_text)
            if not metrics:
                continue
            if metrics["ingredient_coverage"] < 0.30:
                continue
            if metrics["quality_score"] < 0.18:
                continue

            scored_rows.append(
                {
                    "recipe": recipe,
                    "score": metrics["score"],
                    "base_coverage": metrics["base_coverage"],
                    "missing_penalty": metrics["missing_penalty"],
                    "name_similarity": metrics["name_similarity"],
                    "avg_similarity": metrics["avg_similarity"],
                    "quality_score": metrics["quality_score"],
                    "vector_similarity": vector_scores.get(index, 0.0),
                    "tfidf_similarity": tfidf_scores.get(index, 0.0),
                    "ingredient_coverage": metrics["ingredient_coverage"],
                    "matched_recipe_ingredients": metrics["matched_recipe_ingredients"],
                    "missing_recipe_ingredients": metrics["missing_recipe_ingredients"],
                }
            )

        scored_rows.sort(
            key=lambda row: (
                row["score"],
                row["ingredient_coverage"],
                row["avg_similarity"],
                row["vector_similarity"],
                row["tfidf_similarity"],
            ),
            reverse=True,
        )

        results = []
        seen_names = set()
        for row in scored_rows:
            recipe = dict(row["recipe"])
            name_key = self._normalize_text(recipe.get("name"))
            if name_key in seen_names:
                continue
            seen_names.add(name_key)

            coverage_component = float(row["ingredient_coverage"]) * 10.0
            name_component = float(row["name_similarity"]) * 2.2
            similarity_component = float(row["avg_similarity"]) * 2.4
            quality_component = float(row["quality_score"]) * 1.4
            penalty_component = float(row["missing_penalty"]) * 4.0

            explanation = {
                "matched": row["matched_recipe_ingredients"][:12],
                "missing": row["missing_recipe_ingredients"][:12],
                "coverage": round(float(row["base_coverage"]), 4),
                "ranking_score_components": {
                    "coverage_component": round(coverage_component, 4),
                    "similarity_component": round(similarity_component, 4),
                    "name_similarity_component": round(name_component, 4),
                    "quality_component": round(quality_component, 4),
                    "missing_penalty_component": round(penalty_component, 4),
                    "final_score": round(float(row["score"]), 4),
                },
                "reason": self._build_reason_text(
                    coverage=float(row["ingredient_coverage"]),
                    missing_penalty=float(row["missing_penalty"]),
                    avg_similarity=float(row["avg_similarity"]),
                    quality_score=float(row["quality_score"]),
                ),
            }

            enriched = self._enrich_recipe_for_response(
                recipe=recipe,
                explanation=explanation,
                score=row["score"],
            )
            enriched["ingredient_coverage"] = round(float(row["ingredient_coverage"]), 4)
            results.append(enriched)
            if len(results) >= int(limit):
                break

        record_metric("ranking_time_ms", (time.perf_counter() - ranking_started) * 1000.0)
        return tuple(results)

    def get_all_recipes(self):
        return self._recipes

    @lru_cache(maxsize=512)
    def _recipes_by_ingredient_cached(self, normalized_ingredient):
        matches = []
        for recipe in self._recipes:
            ingredients = recipe.get("normalized_ingredients") or []
            if any(self._term_matches_ingredient(normalized_ingredient, item) for item in ingredients):
                matches.append(recipe)
        return tuple(matches)

    def get_recipes_by_ingredient(self, ingredient):
        normalized = normalize_ingredient(ingredient)
        if not normalized:
            return []
        return [self._enrich_recipe_for_response(dict(recipe)) for recipe in self._recipes_by_ingredient_cached(normalized)]

    def get_recipes_by_ingredients(self, ingredients_list):
        weighted = self._prepare_weighted_terms(ingredients_list, None)
        if not weighted:
            return []
        key = tuple(sorted(weighted.items()))
        return [dict(recipe) for recipe in self._recommend_recipes_cached(key, limit=20, use_semantic=False)]

    def recommend_recipes(self, query_terms, limit=5, seed_hint="", term_weights=None, use_semantic=False):
        weighted_terms = self._prepare_weighted_terms(query_terms, term_weights)
        if not weighted_terms:
            return []

        key = tuple(sorted(weighted_terms.items()))
        rows = self._recommend_recipes_cached(key, int(limit), bool(use_semantic))
        return [dict(recipe) for recipe in rows]

    def get_recipe_by_id(self, recipe_id):
        try:
            numeric_id = int(recipe_id)
        except Exception:
            return None
        recipe = self._recipe_by_id.get(numeric_id)
        if not recipe:
            return None
        return self._enrich_recipe_for_response(dict(recipe))

    def process_image(self, image_path):
        from app.ml.ingredient_detector import get_detector

        if not os.path.exists(image_path):
            return {"success": False, "error": "Image not found"}

        detector = get_detector()
        predictions = detector.predict(image_path, top_k=3)
        if not predictions:
            return {"success": False, "error": "No ingredient detected"}

        mapper = get_dish_mapper()
        ingredient_rows = mapper.predictions_to_ingredients(predictions, min_confidence=0.0)
        ingredients = normalize_ingredients_list([row.get("ingredient") for row in ingredient_rows])
        if not ingredients:
            return {
                "success": False,
                "error": "Low model confidence. Please enter ingredients manually for better recommendations.",
            }

        recipes = self.recommend_recipes(
            query_terms=ingredients,
            limit=5,
            term_weights={ingredient: 3.0 for ingredient in ingredients},
        )
        if not recipes:
            return {"success": False, "error": "No recipes found for detected ingredients"}

        return {
            "success": True,
            "detected_food": ingredients[0],
            "confidence": float(predictions[0].get("confidence", 0.0)),
            "recipes": recipes,
        }


recipe_service = RecipeService()


def get_recipe_service():
    return recipe_service

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from threading import Lock
from urllib.parse import quote_plus

import requests

from app.ml.image_validator import get_image_validator
from app.utils.db_utils import get_cached_recipe_image, upsert_recipe_image_cache


logger = logging.getLogger(__name__)

FALLBACK_VEG_IMAGE = "/static/images/recipe_placeholder_veg.svg"
FALLBACK_NON_VEG_IMAGE = "/static/images/recipe_placeholder_nonveg.svg"


class RecipeImageService:
    def __init__(self):
        self.fetch_enabled = str(os.getenv("RECIPE_IMAGE_FETCH_ENABLED", "1")).strip() != "0"
        self.provider = str(os.getenv("RECIPE_IMAGE_PROVIDER", "auto")).strip().lower()
        self.timeout_sec = float(os.getenv("RECIPE_IMAGE_FETCH_TIMEOUT_SEC", "2.0"))
        self.sync_budget_sec = float(os.getenv("RECIPE_IMAGE_SYNC_BUDGET_SEC", "1.1"))

        self.pexels_key = str(os.getenv("PEXELS_API_KEY", "")).strip()
        self.unsplash_key = str(os.getenv("UNSPLASH_ACCESS_KEY", "")).strip()
        self.spoonacular_key = str(os.getenv("SPOONACULAR_API_KEY", "")).strip()

        self._session = requests.Session()
        self._validator = get_image_validator()

        self._queue = ThreadPoolExecutor(max_workers=2, thread_name_prefix="image-fetch")
        self._pending_lock = Lock()
        self._pending_queries = set()

    @staticmethod
    def fallback_for_recipe_type(recipe_type):
        return FALLBACK_NON_VEG_IMAGE if str(recipe_type).lower() == "non-veg" else FALLBACK_VEG_IMAGE

    @lru_cache(maxsize=4096)
    def get_image_for_recipe(self, recipe_name, recipe_type):
        fallback = self.fallback_for_recipe_type(recipe_type)
        query = str(recipe_name or "").strip()
        if not query:
            return fallback, "fallback"

        cached = get_cached_recipe_image(query)
        if cached and cached.get("recipe_image_url"):
            source = str(cached.get("image_source") or "cache")
            verified = int(cached.get("image_verified") or 0)
            logger.info("[image] cache hit '%s' source=%s verified=%s", query, source, verified)
            return str(cached.get("recipe_image_url")), source

        if not self.fetch_enabled:
            return fallback, "fallback"

        image_url, source, verified = self._fetch_and_verify(query, time_budget_sec=self.sync_budget_sec)
        if image_url:
            upsert_recipe_image_cache(
                recipe_name=query,
                recipe_image_url=image_url,
                image_source=source,
                image_verified=verified,
            )
            return image_url, source

        self.enqueue_fetch(query)
        return fallback, "fallback"

    def enqueue_fetch(self, recipe_name):
        clean = str(recipe_name or "").strip().lower()
        if not clean or not self.fetch_enabled:
            return
        with self._pending_lock:
            if clean in self._pending_queries:
                return
            self._pending_queries.add(clean)

        def worker():
            try:
                image_url, source, verified = self._fetch_and_verify(clean, time_budget_sec=max(self.timeout_sec * 2.5, 3.5))
                if image_url:
                    upsert_recipe_image_cache(
                        recipe_name=clean,
                        recipe_image_url=image_url,
                        image_source=source,
                        image_verified=verified,
                    )
            finally:
                with self._pending_lock:
                    self._pending_queries.discard(clean)

        self._queue.submit(worker)

    def _fetch_and_verify(self, query, time_budget_sec):
        providers = self._provider_order()
        started = None
        import time

        started = time.perf_counter()
        for provider in providers:
            if (time.perf_counter() - started) > float(time_budget_sec):
                break
            try:
                if provider == "spoonacular":
                    url = self._fetch_from_spoonacular(query)
                elif provider == "pexels":
                    url = self._fetch_from_pexels(query)
                elif provider == "unsplash":
                    url = self._fetch_from_unsplash(query)
                else:
                    url = None

                if not url:
                    continue

                is_valid = self._validator.validate_recipe_image(query, url)
                if is_valid:
                    logger.info("[image] accepted provider=%s query='%s'", provider, query)
                    return url, provider, True

                logger.info("[image] rejected by CLIP provider=%s query='%s'", provider, query)
            except Exception as exc:
                logger.warning("[image] provider '%s' failed for '%s': %s", provider, query, exc)
        return None, None, False

    def _provider_order(self):
        # Required fallback chain: Spoonacular -> Pexels -> Unsplash -> fallback
        if self.provider in {"spoonacular", "pexels", "unsplash"}:
            ordered = [self.provider]
            for item in ("spoonacular", "pexels", "unsplash"):
                if item not in ordered:
                    ordered.append(item)
            return ordered
        return ["spoonacular", "pexels", "unsplash"]

    def _fetch_from_pexels(self, query):
        if not self.pexels_key:
            return None
        endpoint = "https://api.pexels.com/v1/search"
        params = {"query": f"{query} recipe food", "per_page": 1, "orientation": "landscape"}
        headers = {"Authorization": self.pexels_key}
        response = self._session.get(endpoint, params=params, headers=headers, timeout=self.timeout_sec)
        if response.status_code in {401, 403, 429}:
            logger.warning("[image] pexels rate/authorization issue status=%s", response.status_code)
            return None
        if response.status_code != 200:
            return None
        payload = response.json() or {}
        photos = payload.get("photos") or []
        if not photos:
            return None
        src = (photos[0] or {}).get("src") or {}
        return src.get("large2x") or src.get("large") or src.get("medium")

    def _fetch_from_unsplash(self, query):
        if not self.unsplash_key:
            return None
        endpoint = "https://api.unsplash.com/search/photos"
        params = {"query": f"{query} recipe food", "per_page": 1, "orientation": "landscape"}
        headers = {"Authorization": f"Client-ID {self.unsplash_key}"}
        response = self._session.get(endpoint, params=params, headers=headers, timeout=self.timeout_sec)
        if response.status_code in {401, 403, 429}:
            logger.warning("[image] unsplash rate/authorization issue status=%s", response.status_code)
            return None
        if response.status_code != 200:
            return None
        payload = response.json() or {}
        results = payload.get("results") or []
        if not results:
            return None
        urls = (results[0] or {}).get("urls") or {}
        return urls.get("regular") or urls.get("small") or urls.get("thumb")

    def _fetch_from_spoonacular(self, query):
        if not self.spoonacular_key:
            return None
        endpoint = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            "query": query,
            "number": 1,
            "apiKey": self.spoonacular_key,
            "addRecipeInformation": False,
        }
        response = self._session.get(endpoint, params=params, timeout=self.timeout_sec)
        if response.status_code in {401, 402, 403, 429}:
            logger.warning("[image] spoonacular rate/billing issue status=%s", response.status_code)
            return None
        if response.status_code != 200:
            return None
        payload = response.json() or {}
        results = payload.get("results") or []
        if not results:
            return None
        return (results[0] or {}).get("image")

    @staticmethod
    def placeholder_fetch_command(provider, recipe_name):
        safe_name = quote_plus(str(recipe_name or "recipe"))
        if provider == "pexels":
            return f"https://api.pexels.com/v1/search?query={safe_name}&per_page=1"
        if provider == "unsplash":
            return f"https://api.unsplash.com/search/photos?query={safe_name}&per_page=1"
        return f"https://api.spoonacular.com/recipes/complexSearch?query={safe_name}&number=1"

    def status(self):
        with self._pending_lock:
            pending = len(self._pending_queries)
        return {
            "image_fetch_enabled": bool(self.fetch_enabled),
            "active_image_provider": self.provider if self.provider else "auto",
            "clip_model_loaded": bool(self._validator.loaded),
            "pending_image_jobs": int(pending),
        }


_image_service = None


def get_recipe_image_service():
    global _image_service
    if _image_service is None:
        _image_service = RecipeImageService()
    return _image_service


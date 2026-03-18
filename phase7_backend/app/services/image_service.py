import os
from functools import lru_cache

import requests
from sqlalchemy.orm import Session


UNSPLASH_ACCESS_KEY = os.getenv(
    "UNSPLASH_ACCESS_KEY",
    "KnYLVwyWLdcaiXdwBqQsX1Z4BrjbtT924pf6O5DM6uY",
)
UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"
REQUEST_TIMEOUT_SECONDS = 8
FALLBACK_IMAGE_URL = "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80"


@lru_cache(maxsize=1024)
def get_recipe_image(recipe_name: str) -> str:
    name = (recipe_name or "").strip()
    if not name or not UNSPLASH_ACCESS_KEY:
        return FALLBACK_IMAGE_URL

    try:
        response = requests.get(
            UNSPLASH_SEARCH_URL,
            params={
                "query": f"{name} food",
                "per_page": 1,
                "client_id": UNSPLASH_ACCESS_KEY,
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results") or []
        if results:
            image_url = ((results[0] or {}).get("urls") or {}).get("regular")
            if image_url:
                return image_url
    except requests.RequestException:
        pass
    except ValueError:
        pass

    return FALLBACK_IMAGE_URL


def get_cached_recipe_image_url(recipe, db: Session | None = None) -> str:
    if recipe is None:
        return FALLBACK_IMAGE_URL

    cached_image = (getattr(recipe, "image_url", None) or "").strip()
    if cached_image:
        return cached_image

    image_url = get_recipe_image(recipe.name)
    if db is not None and hasattr(recipe, "image_url"):
        recipe.image_url = image_url
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
    return image_url


def get_recipe_image_url(recipe_name: str | None) -> str:
    name = (recipe_name or "").strip()
    if not name:
        return FALLBACK_IMAGE_URL
    return get_recipe_image(name)

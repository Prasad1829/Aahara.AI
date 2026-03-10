from functools import lru_cache
from urllib.parse import quote

FALLBACK_IMAGE_URL = "https://source.unsplash.com/featured/?indian-food"


def _build_image_url(recipe_name: str) -> str:
    query = quote(recipe_name)
    return f"https://source.unsplash.com/featured/?food,{query}"


@lru_cache(maxsize=1024)
def get_recipe_image_url(recipe_name: str | None) -> str:
    name = (recipe_name or "").strip()
    if not name:
        return FALLBACK_IMAGE_URL
    return _build_image_url(name)

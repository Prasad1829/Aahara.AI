from functools import lru_cache

FALLBACK_IMAGE_URL = "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80"

STATIC_FOOD_IMAGES = {
    "generic": FALLBACK_IMAGE_URL,
    "breakfast": "https://images.unsplash.com/photo-1484723091739-30a097e8f929?auto=format&fit=crop&w=900&q=80",
    "curry": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80",
    "rice": "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?auto=format&fit=crop&w=900&q=80",
    "chickenCurry": "https://images.unsplash.com/photo-1527477396000-e27163b481c2?auto=format&fit=crop&w=900&q=80",
    "fishCurry": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80",
    "eggCurry": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80",
    "vegetables": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=900&q=80",
    "paneer": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?auto=format&fit=crop&w=900&q=80",
    "dessert": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=900&q=80",
    "breadDessert": "https://images.unsplash.com/photo-1514326640560-7d063ef2aed5?auto=format&fit=crop&w=900&q=80",
}

EXACT_RECIPE_IMAGE_KEYS = {
    "aloo gobi": "vegetables",
    "aloo matar": "vegetables",
    "ariselu": "dessert",
    "attu": "breakfast",
    "baingan bharta": "curry",
    "bandar laddu": "dessert",
    "bhindi masala": "vegetables",
    "biryani": "rice",
    "cabbage poriyal": "vegetables",
    "capsicum masala": "vegetables",
    "chana masala": "curry",
    "chicken curry": "chickenCurry",
    "dal tadka": "curry",
    "double ka meetha": "breadDessert",
    "egg curry": "eggCurry",
    "fish curry": "fishCurry",
    "gavvalu": "dessert",
    "gobi masala": "vegetables",
    "jeera aloo": "vegetables",
    "kajjikaya": "dessert",
    "kakinada khaja": "dessert",
    "lemon rice": "rice",
    "methi aloo": "vegetables",
    "mix veg curry": "vegetables",
    "moong dal fry": "curry",
    "mushroom masala": "vegetables",
    "palak paneer": "paneer",
    "palathalikalu": "dessert",
    "paneer butter masala": "paneer",
    "pesarattu": "breakfast",
    "poornalu": "dessert",
    "pootharekulu": "dessert",
    "qubani ka meetha": "dessert",
    "rajma masala": "curry",
    "shahi tukra": "breadDessert",
    "sheer korma": "dessert",
    "tomato onion stir fry": "vegetables",
    "tomato rice": "rice",
    "veg pulao": "rice",
}

STATIC_IMAGE_RULES = [
    (("fish curry",), "fishCurry"),
    (("chicken curry", "butter chicken", "chilli chicken"), "chickenCurry"),
    (("egg curry",), "eggCurry"),
    (("paneer", "tofu"), "paneer"),
    (("biryani", "pulao", "rice", "khichdi"), "rice"),
    (("attu", "pesarattu", "dosa", "omelette", "bhurji"), "breakfast"),
    (("laddu", "khaja", "kajjikaya", "poornalu", "pootharekulu", "gavvalu", "ariselu", "meetha", "dessert", "sweet"), "dessert"),
    (("tukra", "bread pudding"), "breadDessert"),
    (("poriyal", "stir fry", "bhindi", "gobi", "aloo", "matar", "mushroom", "cabbage", "capsicum", "veg"), "vegetables"),
    (("dal", "rajma", "chana", "masala", "curry", "bharta", "kofta", "palak", "gravy"), "curry"),
]


def _normalize_recipe_key(recipe_name: str) -> str:
    tokens = "".join(char.lower() if char.isalnum() or char.isspace() else " " for char in recipe_name)
    return " ".join(tokens.split())


def _build_image_url(recipe_name: str) -> str:
    normalized = _normalize_recipe_key(recipe_name)
    exact_image_key = EXACT_RECIPE_IMAGE_KEYS.get(normalized)
    if exact_image_key:
        return STATIC_FOOD_IMAGES[exact_image_key]

    for keywords, image_key in STATIC_IMAGE_RULES:
        if any(keyword in normalized for keyword in keywords):
            return STATIC_FOOD_IMAGES[image_key]
    return FALLBACK_IMAGE_URL


@lru_cache(maxsize=1024)
def get_recipe_image_url(recipe_name: str | None) -> str:
    name = (recipe_name or "").strip()
    if not name:
        return FALLBACK_IMAGE_URL
    return _build_image_url(name)

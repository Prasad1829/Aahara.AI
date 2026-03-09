import re
from functools import lru_cache


PHRASE_SYNONYMS = {
    "capsicum": "bell pepper",
    "coriander": "cilantro",
    "coriander leaves": "cilantro",
    "chilli": "chili",
    "green chilli": "green chili",
    "red chilli": "red chili",
    "paneer": "cottage cheese",
    "garbanzo": "chickpea",
    "garbanzo bean": "chickpea",
    "garbanzo beans": "chickpea",
    "chana": "chickpea",
    "chole": "chickpea",
    "spring onion": "green onion",
    "scallion": "green onion",
    "scallions": "green onion",
    "curd": "yogurt",
    "hung curd": "greek yogurt",
    "maida": "all purpose flour",
    "atta": "whole wheat flour",
    "shimla mirch": "bell pepper",
    "dhania": "cilantro",
    "mirchi": "chili",
    "tomto": "tomato",
    "potatoes": "potato",
    "tomatoes": "tomato",
    "onions": "onion",
    "fries": "potato",
    "french fries": "potato",
    "chips": "potato",
    "pani puri": "pani puri",
    "golgappa": "pani puri",
    "golgappe": "pani puri",
    "puchka": "pani puri",
    "fuchka": "pani puri",
}

TOKEN_SYNONYMS = {
    "capsicum": "bell",
    "coriander": "cilantro",
    "chilli": "chili",
    "chilies": "chili",
    "chiles": "chili",
    "paneer": "cottage",
    "garbanzo": "chickpea",
    "garbanzos": "chickpea",
    "scallion": "green",
    "scallions": "green",
    "dhaniya": "cilantro",
    "mirchi": "chili",
    "curd": "yogurt",
}

PREPARATION_WORDS = {
    "fresh",
    "dried",
    "dry",
    "chopped",
    "finely",
    "roughly",
    "diced",
    "sliced",
    "crushed",
    "grated",
    "shredded",
    "minced",
    "powdered",
    "powder",
    "ground",
    "toasted",
    "boiled",
    "steamed",
    "fried",
    "roasted",
    "boneless",
    "skinless",
    "large",
    "small",
    "medium",
    "optional",
    "organic",
    "ripe",
    "raw",
    "extra",
    "virgin",
    "plain",
    "whole",
    "halved",
    "halves",
    "pieces",
    "piece",
    "pack",
    "packet",
    "cups",
    "cup",
}

COMMON_UNITS = {
    "tsp",
    "teaspoon",
    "teaspoons",
    "tbsp",
    "tablespoon",
    "tablespoons",
    "cup",
    "cups",
    "c",
    "oz",
    "ounce",
    "ounces",
    "lb",
    "lbs",
    "pound",
    "pounds",
    "g",
    "gram",
    "grams",
    "kg",
    "ml",
    "l",
    "liter",
    "liters",
    "pinch",
    "clove",
    "cloves",
    "slice",
    "slices",
    "can",
    "cans",
    "jar",
    "jars",
}

CONNECTOR_WORDS = {"of", "and", "or", "to", "taste", "for"}


def _sanitize(text):
    value = str(text or "").strip().lower()
    value = value.replace("_", " ").replace("-", " ")
    value = re.sub(r"\([^)]*\)", " ", value)
    value = re.sub(r"[^a-z0-9\s/]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _looks_like_quantity(token):
    if not token:
        return False
    return bool(re.fullmatch(r"\d+([./]\d+)?", token)) or bool(re.fullmatch(r"\d+/\d+", token))


def _simple_singularize(token):
    if len(token) <= 3:
        return token
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("es") and len(token) > 4:
        return token[:-2]
    if token.endswith("s") and len(token) > 3:
        return token[:-1]
    return token


@lru_cache(maxsize=4096)
def normalize_ingredient(term):
    clean = _sanitize(term)
    if not clean:
        return ""

    if clean in PHRASE_SYNONYMS:
        clean = PHRASE_SYNONYMS[clean]

    tokens = []
    for token in clean.split():
        if _looks_like_quantity(token):
            continue
        if token in COMMON_UNITS:
            continue
        if token in CONNECTOR_WORDS and not tokens:
            continue
        token = _simple_singularize(token)
        token = TOKEN_SYNONYMS.get(token, token)
        if token in PREPARATION_WORDS:
            continue
        tokens.append(token)

    normalized = " ".join(tokens).strip()
    normalized = PHRASE_SYNONYMS.get(normalized, normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def normalize_ingredients_list(values):
    normalized = []
    seen = set()
    for item in values or []:
        token = normalize_ingredient(item)
        if not token or token in seen:
            continue
        seen.add(token)
        normalized.append(token)
    return normalized


def extract_base_ingredient(raw_text):
    clean = _sanitize(raw_text)
    if not clean:
        return ""

    tokens = []
    for token in clean.split():
        if _looks_like_quantity(token):
            continue
        if token in COMMON_UNITS:
            continue
        if token in CONNECTOR_WORDS and not tokens:
            continue
        tokens.append(token)

    return normalize_ingredient(" ".join(tokens))

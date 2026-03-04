ALIASES = {
    # Language / spelling variants
    "aloo": "potato",
    "baingan": "eggplant",
    "bhindi": "okra",
    "ladyfinger": "okra",
    "lady finger": "okra",
    "ladys finger": "okra",
    "lady's finger": "okra",
    "mirchi": "chili",
    "chilli": "chili",
    "green chilli": "chili",
    "red chilli powder": "chili powder",
    "haldi": "turmeric",
    "dhania powder": "coriander powder",
    "dhania": "coriander",
    "jeera": "cumin",
    "rai": "mustard seeds",
    "adrak": "ginger",
    "lahsun": "garlic",
    "dahi": "yogurt",
    "curd": "yogurt",
    "gobhi": "cauliflower",
    "matar": "peas",
    "shimla mirch": "capsicum",
    "besan": "gram flour",
    "suji": "semolina",
    "rava": "semolina",
    "tur dal": "toor dal",
    "arhar dal": "toor dal",
    "moong": "moong dal",
    "masoor": "masoor dal",
    "chana": "chana dal",
    "kala chana": "black chana",
    "kabuli chana": "chickpeas",
    "lobiya": "lobia",
    "sarson oil": "mustard oil",
    "moongfali oil": "groundnut oil",
    "nariyal tel": "coconut oil",
    "tamatar": "tomato",
    "pyaaz": "onion",
    "anda": "egg",
}


INDIAN_INGREDIENT_CLASSES = {
    # Vegetables
    "onion", "tomato", "potato", "carrot", "cucumber", "eggplant", "okra",
    "capsicum", "garlic", "ginger", "cabbage", "cauliflower", "peas", "beans",
    "spinach", "methi", "drumstick", "beetroot", "bottle gourd", "ridge gourd",
    "pumpkin", "ash gourd", "radish", "turnip", "yam", "sweet potato", "corn",
    "mushroom", "broccoli", "zucchini",

    # Fruits often used in Indian food
    "lemon", "raw mango", "banana", "coconut", "tamarind", "amla", "pomegranate",

    # Grains / flour
    "rice", "basmati rice", "wheat flour", "atta", "maida", "semolina", "poha",
    "vermicelli", "flattened rice", "gram flour", "millet", "ragi", "jowar", "bajra",

    # Pulses / legumes
    "toor dal", "moong dal", "chana dal", "masoor dal", "urad dal", "rajma",
    "chickpeas", "black chana", "lobia", "green gram", "soy chunks", "peas protein",

    # Dairy
    "milk", "yogurt", "paneer", "butter", "ghee", "cream", "cheese", "khoya",

    # Oils and fats
    "oil", "sunflower oil", "groundnut oil", "mustard oil", "coconut oil",
    "sesame oil", "olive oil",

    # Whole spices
    "cumin", "mustard seeds", "fenugreek seeds", "fennel seeds", "nigella seeds",
    "ajwain", "carom seeds", "hing", "asafoetida", "cloves", "cardamom", "cinnamon",
    "bay leaf", "black pepper", "star anise", "nutmeg", "mace",

    # Spice powders / blends
    "salt", "turmeric", "chili powder", "coriander powder", "garam masala",
    "cumin powder", "black salt", "kashmiri chili powder", "sambar powder",
    "rasam powder", "kitchen king masala", "chaat masala", "kasuri methi",
    "amchur", "dry mango powder",

    # Herbs / aromatics
    "coriander", "mint", "curry leaves", "green chili", "ginger garlic paste",

    # Proteins (non-veg)
    "egg", "chicken", "mutton", "fish", "prawns",
}


def normalize_ingredient(value: str) -> str:
    normalized = value.lower().strip()
    return ALIASES.get(normalized, normalized)

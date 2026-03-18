const RECIPE_PHOTO_URLS = {
  generic: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80",
  breakfast: "https://images.unsplash.com/photo-1484723091739-30a097e8f929?auto=format&fit=crop&w=900&q=80",
  curry: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80",
  rice: "https://unsplash.com/photos/aq8v45EwCa0/download?force=true&w=900",
  chickenCurry: "https://unsplash.com/photos/gwUA_pHaOYY/download?force=true&w=900",
  fishCurry: "https://unsplash.com/photos/7v9U94719TE/download?force=true&w=900",
  eggCurry: "https://unsplash.com/photos/h51fYRG2p30/download?force=true&w=900",
  vegetables: "https://unsplash.com/photos/aq8v45EwCa0/download?force=true&w=900",
  paneer: "https://unsplash.com/photos/vgTntT8PmIM/download?force=true&w=900",
  dessert: "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=900&q=80",
  breadDessert: "https://images.unsplash.com/photo-1514326640560-7d063ef2aed5?auto=format&fit=crop&w=900&q=80",
};

const EXACT_RECIPE_THEME_KEYS = {
  "aloo gobi": "vegetables",
  "aloo matar": "vegetables",
  ariselu: "dessert",
  attu: "breakfast",
  "baingan bharta": "curry",
  "bandar laddu": "dessert",
  "bhindi masala": "vegetables",
  biryani: "rice",
  "cabbage poriyal": "vegetables",
  "capsicum masala": "vegetables",
  "chana masala": "curry",
  "chicken curry": "chickenCurry",
  "dal tadka": "curry",
  "double ka meetha": "breadDessert",
  "egg curry": "eggCurry",
  "fish curry": "fishCurry",
  gavvalu: "dessert",
  "gobi masala": "vegetables",
  "jeera aloo": "vegetables",
  kajjikaya: "dessert",
  "kakinada khaja": "dessert",
  "lemon rice": "rice",
  "methi aloo": "vegetables",
  "mix veg curry": "vegetables",
  "moong dal fry": "curry",
  "mushroom masala": "vegetables",
  "palak paneer": "paneer",
  palathalikalu: "dessert",
  "paneer butter masala": "paneer",
  pesarattu: "breakfast",
  poornalu: "dessert",
  pootharekulu: "dessert",
  "qubani ka meetha": "dessert",
  "rajma masala": "curry",
  "shahi tukra": "breadDessert",
  "sheer korma": "dessert",
  "tomato onion stir fry": "vegetables",
  "tomato rice": "rice",
  "veg pulao": "rice",
};

const CATEGORY_RULES = [
  { keywords: ["fish curry"], imageKey: "fishCurry" },
  { keywords: ["chicken curry", "butter chicken", "chilli chicken"], imageKey: "chickenCurry" },
  { keywords: ["egg curry"], imageKey: "eggCurry" },
  { keywords: ["paneer", "tofu"], imageKey: "paneer" },
  { keywords: ["biryani", "pulao", "rice", "khichdi"], imageKey: "rice" },
  { keywords: ["attu", "pesarattu", "dosa", "omelette", "bhurji"], imageKey: "breakfast" },
  { keywords: ["laddu", "khaja", "kajjikaya", "poornalu", "pootharekulu", "gavvalu", "ariselu", "meetha", "dessert", "sweet"], imageKey: "dessert" },
  { keywords: ["tukra", "bread pudding"], imageKey: "breadDessert" },
  { keywords: ["poriyal", "stir fry", "bhindi", "gobi", "aloo", "matar", "mushroom", "cabbage", "capsicum", "veg"], imageKey: "vegetables" },
  { keywords: ["dal", "rajma", "chana", "masala", "curry", "bharta", "kofta", "palak", "gravy"], imageKey: "curry" },
];

function normalizeName(name = "") {
  return String(name || "Recipe").trim().replace(/\s+/g, " ");
}

function normalizeRecipeKey(name = "") {
  return normalizeName(name)
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function normalizeIngredients(ingredients = []) {
  if (Array.isArray(ingredients)) {
    return ingredients
      .filter(Boolean)
      .map((item) => String(item).trim())
      .filter(Boolean);
  }
  if (!ingredients) {
    return [];
  }
  return [String(ingredients).trim()].filter(Boolean);
}

function buildRecipeQueryImage(name = "", ingredients = [], themeKey = "generic") {
  const recipeName = normalizeRecipeKey(name).replace(/\s+/g, ",");
  const ingredientTerms = normalizeIngredients(ingredients)
    .slice(0, 3)
    .map((item) => item.toLowerCase().replace(/\s+/g, ","))
    .join(",");
  const themeTerm = String(themeKey || "indian food").replace(/([A-Z])/g, " $1").toLowerCase().trim().replace(/\s+/g, ",");
  const searchTerms = ["indian-food", recipeName, ingredientTerms, themeTerm].filter(Boolean).join(",");
  return `https://source.unsplash.com/featured/320x320/?${searchTerms}`;
}

function getRecipeThemeKey(name = "", ingredients = []) {
  const recipeKey = normalizeRecipeKey(name);
  if (EXACT_RECIPE_THEME_KEYS[recipeKey]) {
    return EXACT_RECIPE_THEME_KEYS[recipeKey];
  }

  const normalized = `${recipeKey} ${normalizeIngredients(ingredients).join(" ").toLowerCase()}`.trim();
  for (const rule of CATEGORY_RULES) {
    if (rule.keywords.some((keyword) => normalized.includes(keyword))) {
      return rule.imageKey;
    }
  }
  return "generic";
}

export function getRecipePlaceholderImage(name = "", ingredients = []) {
  const themeKey = getRecipeThemeKey(name, ingredients);
  return buildRecipeQueryImage(name, ingredients, themeKey);
}

export function getRecipeImageSources(name = "", ingredients = []) {
  const themeKey = getRecipeThemeKey(name, ingredients);
  return [
    buildRecipeQueryImage(name, ingredients, themeKey),
    RECIPE_PHOTO_URLS[themeKey] || RECIPE_PHOTO_URLS.generic,
    RECIPE_PHOTO_URLS.generic,
  ];
}

export function getRecipeImage(name = "", ingredients = []) {
  return getRecipeImageSources(name, ingredients)[0];
}

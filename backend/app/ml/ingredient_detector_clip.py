import os

from PIL import Image

from app.ml.ingredient_normalizer import normalize_ingredient


CLIP_MODEL_NAME = "openai/clip-vit-base-patch32"
DEFAULT_TOP_K = 8
DEFAULT_MIN_CONFIDENCE = 0.10

# 180 common ingredient labels for zero-shot CLIP matching.
INGREDIENT_LABELS = [
    "apple",
    "apricot",
    "artichoke",
    "asparagus",
    "avocado",
    "bacon",
    "bagel",
    "basil",
    "bay leaf",
    "bean",
    "bean sprout",
    "beef",
    "beetroot",
    "bell pepper",
    "black pepper",
    "black sesame",
    "blue cheese",
    "blueberry",
    "bok choy",
    "bread",
    "broccoli",
    "broth",
    "brown rice",
    "brown sugar",
    "brussels sprout",
    "buckwheat",
    "bun",
    "butter",
    "buttermilk",
    "cabbage",
    "caper",
    "capsicum",
    "carrot",
    "cashew",
    "cauliflower",
    "celery",
    "chard",
    "cheddar",
    "cheese",
    "cherry",
    "chia seed",
    "chicken",
    "chickpea",
    "chili",
    "chili powder",
    "chive",
    "chocolate",
    "cilantro",
    "cinnamon",
    "clove",
    "cocoa powder",
    "coconut",
    "coconut milk",
    "cod",
    "coriander",
    "corn",
    "corn flour",
    "cornmeal",
    "cottage cheese",
    "cream",
    "crouton",
    "cucumber",
    "cumin",
    "curry leaf",
    "curry powder",
    "dill",
    "duck",
    "egg",
    "eggplant",
    "fennel",
    "feta",
    "fig",
    "fish",
    "flour",
    "garbanzo bean",
    "garlic",
    "ginger",
    "goat cheese",
    "gochujang",
    "grape",
    "grapefruit",
    "green bean",
    "green onion",
    "ham",
    "hazelnut",
    "honey",
    "jalapeno",
    "kale",
    "ketchup",
    "kidney bean",
    "kimchi",
    "kiwi",
    "lamb",
    "leek",
    "lemon",
    "lentil",
    "lettuce",
    "lime",
    "lobster",
    "mango",
    "maple syrup",
    "mayonnaise",
    "milk",
    "mint",
    "miso",
    "mozzarella",
    "mushroom",
    "mustard",
    "mustard seed",
    "noodle",
    "nutmeg",
    "oat",
    "oatmeal",
    "octopus",
    "olive",
    "olive oil",
    "onion",
    "orange",
    "oregano",
    "paprika",
    "parsley",
    "parmesan",
    "pasta",
    "pea",
    "peach",
    "peanut",
    "pear",
    "peppercorn",
    "pickle",
    "pineapple",
    "pistachio",
    "pork",
    "potato",
    "prawn",
    "prosciutto",
    "pumpkin",
    "pumpkin seed",
    "quinoa",
    "radish",
    "raisin",
    "raspberry",
    "red onion",
    "rice",
    "rice noodle",
    "ricotta",
    "rosemary",
    "rye flour",
    "saffron",
    "sage",
    "salmon",
    "salt",
    "sausage",
    "scallion",
    "seaweed",
    "sesame",
    "sesame oil",
    "shallot",
    "shrimp",
    "soy sauce",
    "spinach",
    "spring onion",
    "squash",
    "steak",
    "strawberry",
    "sugar",
    "sunflower seed",
    "sweet potato",
    "tahini",
    "tamarind",
    "thyme",
    "tofu",
    "tomato",
    "tortilla",
    "trout",
    "tuna",
    "turkey",
    "turmeric",
    "vanilla",
    "vinegar",
    "walnut",
    "wasabi",
    "watercress",
    "wheat flour",
    "white pepper",
    "whole wheat flour",
    "yeast",
    "yogurt",
    "zucchini",
]


def _resolve_clip_model_source(local_only):
    configured = (
        str(os.getenv("CLIP_MODEL_NAME_OR_PATH", "")).strip()
        or str(os.getenv("CLIP_MODEL_PATH", "")).strip()
    )
    if configured:
        return configured

    if local_only:
        project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        workspace_dir = os.path.abspath(os.path.join(project_dir, ".."))
        roots = [
            str(os.getenv("DATASET_ROOT", "")).strip(),
            str(os.getenv("RECIPE_DATASET_ROOT", "")).strip(),
            os.path.join(workspace_dir, "dataset"),
            os.path.join(project_dir, "dataset"),
            os.path.join(project_dir, "backend", "dataset"),
        ]
        seen = set()
        for root in roots:
            if not root:
                continue
            clean_root = os.path.abspath(os.path.expanduser(root))
            if clean_root in seen:
                continue
            seen.add(clean_root)
            candidate = os.path.join(clean_root, "hf_models", "clip-vit-base-patch32")
            if os.path.isdir(candidate):
                return candidate

    return CLIP_MODEL_NAME


class ClipIngredientDetector:
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = "cpu"
        self.model_error = None
        self.prompt_labels = [normalize_ingredient(label) or label for label in INGREDIENT_LABELS]
        self.prompt_texts = [f"a photo of {label}" for label in self.prompt_labels]
        self._load_model()

    def _load_model(self):
        try:
            import torch
            from transformers import CLIPModel, CLIPProcessor

            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            local_only = str(os.getenv("CLIP_LOCAL_FILES_ONLY", "0")).strip() != "0"
            model_source = _resolve_clip_model_source(local_only=local_only)
            self.processor = CLIPProcessor.from_pretrained(model_source, local_files_only=local_only)
            self.model = CLIPModel.from_pretrained(model_source, local_files_only=local_only).to(self.device)
            self.model.eval()
        except Exception as exc:
            self.model = None
            self.processor = None
            self.model_error = str(exc)
            print(f"[!] CLIP detector unavailable: {exc}")

    def detect_ingredients(self, image_path, top_k=DEFAULT_TOP_K, min_confidence=DEFAULT_MIN_CONFIDENCE):
        if self.model is None or self.processor is None:
            return []

        try:
            import torch

            with Image.open(image_path) as image:
                rgb = image.convert("RGB")

            inputs = self.processor(
                text=self.prompt_texts,
                images=rgb,
                return_tensors="pt",
                padding=True,
            )
            inputs = {key: value.to(self.device) for key, value in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits_per_image[0]
                probabilities = torch.softmax(logits, dim=0)

            top_k = max(1, min(int(top_k), len(self.prompt_labels)))
            scores, indices = torch.topk(probabilities, k=top_k)

            rows = []
            for score, index in zip(scores.tolist(), indices.tolist()):
                confidence = float(score)
                if confidence < float(min_confidence):
                    continue
                label = self.prompt_labels[int(index)]
                rows.append(
                    {
                        "ingredient": label,
                        "confidence": round(confidence, 4),
                        "source": "clip",
                    }
                )
            return rows
        except Exception as exc:
            self.model_error = str(exc)
            print(f"[!] CLIP detect error: {exc}")
            return []


_clip_detector = None


def get_clip_detector():
    global _clip_detector
    if _clip_detector is None:
        _clip_detector = ClipIngredientDetector()
    return _clip_detector

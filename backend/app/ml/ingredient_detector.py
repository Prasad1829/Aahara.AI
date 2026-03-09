import logging
import os
from functools import lru_cache

from app.ml.ingredient_normalizer import normalize_ingredient


logger = logging.getLogger(__name__)

YOLO_DEFAULT_MODEL = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")
YOLO_MIN_CONFIDENCE = float(os.getenv("YOLO_MIN_CONFIDENCE", "0.4"))

# COCO-like food labels mapped to ingredient-style tokens.
YOLO_FOOD_CLASS_MAP = {
    "apple": "apple",
    "banana": "banana",
    "orange": "orange",
    "broccoli": "broccoli",
    "carrot": "carrot",
    "hot dog": "sausage",
    "pizza": "cheese",
    "sandwich": "bread",
    "cake": "flour",
    "donut": "flour",
}


def _resolve_yolo_model_path(path_value):
    raw = str(path_value or "").strip() or "yolov8n.pt"
    if os.path.isabs(raw) and os.path.exists(raw):
        return raw
    if os.path.exists(raw):
        return os.path.abspath(raw)

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
        for candidate in (
            os.path.join(clean_root, "models", raw),
            os.path.join(clean_root, raw),
        ):
            if os.path.exists(candidate):
                return candidate

    # Fall back to original name; ultralytics will attempt to auto-download if needed.
    return raw


class IngredientDetector:
    def __init__(self):
        self.model = None
        self.model_error = None
        self.model_path = _resolve_yolo_model_path(YOLO_DEFAULT_MODEL)
        self._ultralytics = None

    def _ensure_model(self):
        if self.model is not None:
            return True
        if self.model_error:
            return False
        try:
            from ultralytics import YOLO

            self._ultralytics = YOLO
            self.model = YOLO(self.model_path)
            return True
        except Exception as exc:
            self.model_error = str(exc)
            logger.warning("[yolo] detector unavailable: %s", exc)
            return False

    @property
    def loaded(self):
        return self.model is not None

    def status(self):
        return {
            "loaded": bool(self.loaded),
            "model_path": self.model_path,
            "error": self.model_error,
        }

    def _class_name_from_index(self, names, class_index):
        if isinstance(names, dict):
            return str(names.get(int(class_index), "")).strip().lower()
        if isinstance(names, (list, tuple)):
            index = int(class_index)
            if 0 <= index < len(names):
                return str(names[index]).strip().lower()
        return ""

    @staticmethod
    def _normalize_label(label):
        text = str(label or "").strip().lower()
        if not text:
            return ""
        mapped = YOLO_FOOD_CLASS_MAP.get(text, text)
        normalized = normalize_ingredient(mapped)
        return normalized or ""

    @lru_cache(maxsize=2048)
    def _predict_cached(self, image_path, top_k):
        if not self._ensure_model():
            return []
        try:
            results = self.model.predict(source=image_path, verbose=False)
            if not results:
                return []

            result = results[0]
            boxes = getattr(result, "boxes", None)
            names = getattr(result, "names", {})
            if boxes is None:
                return []

            rows = []
            for box in boxes:
                try:
                    confidence = float(box.conf[0].item())
                    class_index = int(box.cls[0].item())
                except Exception:
                    continue

                if confidence < YOLO_MIN_CONFIDENCE:
                    continue

                class_name = self._class_name_from_index(names, class_index)
                ingredient = self._normalize_label(class_name)
                if not ingredient:
                    continue

                rows.append(
                    {
                        "ingredient": ingredient,
                        "confidence": round(confidence, 4),
                        "class_index": class_index,
                        "source": "yolo",
                    }
                )
                logger.info("[yolo] detected=%s confidence=%.4f", ingredient, confidence)

            # Deduplicate by ingredient keeping highest confidence
            by_name = {}
            for row in rows:
                key = row["ingredient"]
                if key not in by_name or row["confidence"] > by_name[key]["confidence"]:
                    by_name[key] = row

            deduped = sorted(by_name.values(), key=lambda item: item["confidence"], reverse=True)
            return deduped[: max(1, int(top_k))]
        except Exception as exc:
            self.model_error = str(exc)
            logger.warning("[yolo] prediction error: %s", exc)
            return []

    def detect_ingredients(self, image_path, top_k=5):
        return self._predict_cached(str(image_path), int(top_k))

    def detect(self, image_path):
        rows = self.detect_ingredients(image_path, top_k=1)
        if rows:
            return rows[0]
        return {"ingredient": "error", "confidence": 0.0, "error": self.model_error or "no_detection"}

    def predict(self, image_path, top_k=3):
        return self.detect_ingredients(image_path, top_k=top_k)


_detector = None


def get_detector():
    global _detector
    if _detector is None:
        _detector = IngredientDetector()
    return _detector

import io
import logging
import os
from functools import lru_cache

import requests
from PIL import Image


logger = logging.getLogger(__name__)

CLIP_MODEL_NAME = "openai/clip-vit-base-patch32"
DEFAULT_CLIP_THRESHOLD = 0.25


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


class ClipImageValidator:
    def __init__(self):
        self.model = None
        self.processor = None
        self.torch = None
        self.device = "cpu"
        self.model_error = None
        self.threshold = float(os.getenv("CLIP_IMAGE_SIMILARITY_THRESHOLD", str(DEFAULT_CLIP_THRESHOLD)))
        self.timeout_sec = float(os.getenv("RECIPE_IMAGE_FETCH_TIMEOUT_SEC", "2.0"))
        self._session = requests.Session()
        self._load_attempted = False

    def _load_model(self):
        try:
            import torch
            from transformers import CLIPModel, CLIPProcessor

            self.torch = torch
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
            logger.warning("[clip-validator] unavailable: %s", exc)

    @property
    def loaded(self):
        return self.model is not None and self.processor is not None

    def _ensure_model(self):
        if self.loaded:
            return True
        if self._load_attempted and not self.loaded:
            return False
        self._load_attempted = True
        self._load_model()
        return self.loaded

    @lru_cache(maxsize=4096)
    def validate_recipe_image(self, recipe_name, image_url):
        if not self._ensure_model():
            logger.warning("[clip-validator] model not loaded; rejecting image for '%s'", recipe_name)
            return False

        name = str(recipe_name or "").strip()
        url = str(image_url or "").strip()
        if not name or not url:
            return False

        try:
            response = self._session.get(url, timeout=self.timeout_sec)
            if response.status_code != 200:
                return False

            with Image.open(io.BytesIO(response.content)) as img:
                rgb = img.convert("RGB")

            prompt = f"a food recipe photo of {name}"
            inputs = self.processor(text=[prompt], images=rgb, return_tensors="pt", padding=True)
            inputs = {key: value.to(self.device) for key, value in inputs.items()}

            with self.torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits_per_image[0]
                probs = self.torch.softmax(logits, dim=0)
                similarity = float(probs[0].item())

            is_valid = similarity >= float(self.threshold)
            logger.info(
                "[clip-validator] recipe='%s' similarity=%.4f threshold=%.2f valid=%s",
                name,
                similarity,
                self.threshold,
                is_valid,
            )
            return is_valid
        except Exception as exc:
            logger.warning("[clip-validator] error for '%s': %s", name, exc)
            return False


_validator = None


def get_image_validator():
    global _validator
    if _validator is None:
        _validator = ClipImageValidator()
    return _validator


def validate_recipe_image(recipe_name, image_url):
    validator = get_image_validator()
    return validator.validate_recipe_image(recipe_name, image_url)

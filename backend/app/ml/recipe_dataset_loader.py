import json
import logging
import os


logger = logging.getLogger(__name__)


class RecipeDatasetLoader:
    def __init__(self):
        self.primary_path = (
            os.getenv("RECIPE_PRIMARY_DATASET_PATH", "").strip()
            or os.getenv("RECIPE1M_DATASET_PATH", "").strip()
        )
        self.enabled = str(os.getenv("RECIPE_DATASET_ENABLED", "1")).strip() != "0"
        self.max_rows = int(os.getenv("RECIPE_DATASET_MAX_ROWS", "120000"))

    @staticmethod
    def _normalize_row(raw, fallback_id):
        if not isinstance(raw, dict):
            return None

        name = str(raw.get("title") or raw.get("name") or "").strip()
        if not name:
            return None

        ingredients = raw.get("ingredients") or raw.get("ingredient_lines") or raw.get("ingredientLines") or []
        if isinstance(ingredients, str):
            ingredients = [item.strip() for item in ingredients.split(",") if item.strip()]
        elif isinstance(ingredients, list):
            ingredients = [str(item).strip() for item in ingredients if str(item).strip()]
        else:
            ingredients = []

        instructions = raw.get("instructions") or raw.get("directions") or raw.get("steps") or []
        if isinstance(instructions, str):
            instructions = [line.strip() for line in instructions.split("\n") if line.strip()]
        elif isinstance(instructions, list):
            normalized_steps = []
            for step in instructions:
                if isinstance(step, dict):
                    text = str(step.get("text") or step.get("instruction") or "").strip()
                else:
                    text = str(step).strip()
                if text:
                    normalized_steps.append(text)
            instructions = normalized_steps
        else:
            instructions = []

        cooking_time = raw.get("cooking_time") or raw.get("total_time") or raw.get("readyInMinutes")
        image_url = raw.get("image_url") or raw.get("image")

        try:
            recipe_id = int(raw.get("id"))
        except Exception:
            recipe_id = int(fallback_id)

        return {
            "id": recipe_id,
            "name": name,
            "ingredients": ingredients,
            "instructions": instructions,
            "cook_time": cooking_time,
            "image_url": image_url,
        }

    def _load_json_list(self, path):
        with open(path, "r", encoding="utf-8") as file_obj:
            payload = json.load(file_obj)
        if not isinstance(payload, list):
            return []
        rows = []
        for idx, raw in enumerate(payload):
            if len(rows) >= self.max_rows:
                break
            row = self._normalize_row(raw, fallback_id=10_000_000 + idx)
            if row:
                rows.append(row)
        return rows

    def _load_json_lines(self, path):
        rows = []
        with open(path, "r", encoding="utf-8") as file_obj:
            for idx, line in enumerate(file_obj):
                if len(rows) >= self.max_rows:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    raw = json.loads(line)
                except Exception:
                    continue
                row = self._normalize_row(raw, fallback_id=10_000_000 + idx)
                if row:
                    rows.append(row)
        return rows

    @staticmethod
    def _base_dirs():
        # .../ingredient_recipe_ai/backend/app/ml -> .../ingredient_recipe_ai
        project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        workspace_dir = os.path.abspath(os.path.join(project_dir, ".."))
        env_roots = [
            str(os.getenv("DATASET_ROOT", "")).strip(),
            str(os.getenv("RECIPE_DATASET_ROOT", "")).strip(),
        ]
        candidates = []
        for value in env_roots:
            if value:
                candidates.append(os.path.abspath(os.path.expanduser(value)))
        candidates.extend(
            [
                os.path.join(workspace_dir, "dataset"),
                os.path.join(project_dir, "dataset"),
                os.path.join(project_dir, "backend", "dataset"),
            ]
        )
        unique = []
        seen = set()
        for path in candidates:
            clean = os.path.abspath(path)
            if clean in seen:
                continue
            seen.add(clean)
            unique.append(clean)
        return unique

    def _resolve_primary_path(self):
        raw = str(self.primary_path or "").strip()
        if not raw:
            return "", []

        candidates = [os.path.abspath(os.path.expanduser(raw))]
        if not os.path.isabs(raw):
            for base_dir in self._base_dirs():
                candidates.append(os.path.abspath(os.path.join(base_dir, raw)))

        unique = []
        seen = set()
        for path in candidates:
            if path in seen:
                continue
            seen.add(path)
            unique.append(path)

        for path in unique:
            if os.path.exists(path):
                return path, unique
        return unique[0], unique

    def load_primary_recipes(self):
        if not self.enabled or not self.primary_path:
            return []
        path, checked = self._resolve_primary_path()
        if not os.path.exists(path):
            logger.warning("[dataset] Primary dataset path not found: %s (checked=%s)", path, checked)
            return []

        try:
            ext = os.path.splitext(path)[1].lower()
            if ext == ".json":
                rows = self._load_json_list(path)
            else:
                rows = self._load_json_lines(path)
            logger.info("[dataset] loaded primary recipes: %s (%d rows)", path, len(rows))
            return rows
        except Exception as exc:
            logger.warning("[dataset] failed to load primary dataset %s: %s", path, exc)
            return []


_loader = None


def get_recipe_dataset_loader():
    global _loader
    if _loader is None:
        _loader = RecipeDatasetLoader()
    return _loader

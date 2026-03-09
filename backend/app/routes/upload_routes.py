import os
import re
import time
import logging

import numpy as np
from flask import Blueprint, current_app, jsonify, request, session
from PIL import Image
from werkzeug.utils import secure_filename

from app.ml.dish_mapper import get_dish_mapper
from app.ml.ingredient_detector import get_detector
from app.ml.ingredient_detector_clip import get_clip_detector
from app.ml.ingredient_normalizer import normalize_ingredient
from app.services.recipe_service import get_recipe_service
from app.utils.db_utils import log_audit_event, log_detection_history
from app.utils.system_metrics import record_metric


upload_bp = Blueprint("upload", __name__)
recipe_service = get_recipe_service()
dish_mapper = get_dish_mapper()
logger = logging.getLogger(__name__)

MIN_MODEL_CONFIDENCE = 0.30
MODEL_RELATIVE_THRESHOLD = 0.55
MODEL_ONLY_MIN_CONFIDENCE = 0.52
MAX_MODEL_LABELS = 4

CLIP_CONFIDENT_THRESHOLD = 0.20
CLIP_MIN_CONFIDENCE = 0.08

SOURCE_WEIGHTS = {
    "typed": 5.0,
    "clip": 4.0,
    "ocr": 3.0,
    "filename": 2.0,
    "image": 1.0,
    "vision_heuristic": 1.0,
    "model_guess": 1.0,
}

NOISE_FILENAME_TOKENS = {
    "img",
    "image",
    "photo",
    "pic",
    "picture",
    "screenshot",
    "camera",
    "capture",
    "oip",
    "packet",
    "snap",
    "whatsapp",
    "download",
    "new",
    "copy",
    "final",
    "jpeg",
    "jpg",
    "png",
}


def _normalize_text(text):
    clean = str(text or "").strip().lower().replace("-", " ")
    clean = re.sub(r"[^a-z0-9_\s]", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def _dedupe_keep_order(values):
    ordered = []
    seen = set()
    for value in values or []:
        normalized = normalize_ingredient(value)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered


def _extract_filename_terms(filename):
    if not filename:
        return []
    name_root, _ = os.path.splitext(str(filename).lower())
    raw_tokens = [
        token
        for token in re.split(r"[^a-z0-9]+", name_root)
        if len(token) >= 3 and not token.isdigit() and token not in NOISE_FILENAME_TOKENS
    ]
    return _dedupe_keep_order(raw_tokens)


def _select_model_predictions(raw_predictions):
    candidates = []
    for item in raw_predictions or []:
        dish_label = _normalize_text(item.get("ingredient"))
        if not dish_label:
            continue
        try:
            confidence = float(item.get("confidence", 0.0))
        except Exception:
            confidence = 0.0
        candidates.append({"ingredient": dish_label, "confidence": confidence, "source": "model"})

    if not candidates:
        return []

    candidates.sort(key=lambda row: row["confidence"], reverse=True)
    top_confidence = candidates[0]["confidence"]
    if top_confidence < MIN_MODEL_CONFIDENCE:
        return candidates[:1]

    minimum_confidence = max(top_confidence * MODEL_RELATIVE_THRESHOLD, 0.10)
    filtered = [row for row in candidates if row["confidence"] >= minimum_confidence]
    return filtered[:MAX_MODEL_LABELS] or candidates[:1]


def _infer_visual_terms(image_path):
    try:
        image = Image.open(image_path).convert("RGB").resize((256, 256))
        pixels = np.array(image)
    except Exception:
        return []

    if pixels.size == 0:
        return []

    white_mask = (
        (pixels[:, :, 0] >= 245)
        & (pixels[:, :, 1] >= 245)
        & (pixels[:, :, 2] >= 245)
    )
    white_ratio = float(np.mean(white_mask))
    non_bg_pixels = pixels[~white_mask]
    if len(non_bg_pixels) < 800:
        return []

    r = non_bg_pixels[:, 0].astype(np.float32)
    g = non_bg_pixels[:, 1].astype(np.float32)
    b = non_bg_pixels[:, 2].astype(np.float32)

    potato_like = (
        (r >= 110)
        & (r <= 235)
        & (g >= 90)
        & (g <= 215)
        & (b >= 60)
        & (b <= 185)
        & (np.abs(r - g) <= 75)
    )
    red_like = (r > 150) & (g < 130) & (b < 130)

    potato_ratio = float(np.mean(potato_like))
    red_ratio = float(np.mean(red_like))

    if white_ratio >= 0.15 and potato_ratio >= 0.30 and red_ratio <= 0.11:
        confidence = round(min(0.88, 0.52 + (potato_ratio * 0.45)), 3)
        return [{"ingredient": "potato", "confidence": confidence, "source": "vision_heuristic"}]

    return []


def _safe_confidence(value, fallback=0.0):
    try:
        return float(value)
    except Exception:
        return float(fallback)


def _merge_detected_entry(store, ingredient, source, confidence):
    normalized = normalize_ingredient(ingredient)
    if not normalized:
        return

    confidence = round(_safe_confidence(confidence, 0.0), 4)
    current = store.get(normalized)
    if current is None:
        store[normalized] = {
            "ingredient": normalized,
            "confidence": confidence,
            "source": source,
        }
        return

    existing_source_weight = SOURCE_WEIGHTS.get(current.get("source"), 1.0)
    new_source_weight = SOURCE_WEIGHTS.get(source, 1.0)
    if new_source_weight > existing_source_weight or confidence > float(current.get("confidence", 0.0)):
        store[normalized] = {
            "ingredient": normalized,
            "confidence": confidence,
            "source": source,
        }


def _add_weighted_term(weight_map, term, source, confidence=1.0):
    normalized = normalize_ingredient(term)
    if not normalized:
        return

    base_weight = float(SOURCE_WEIGHTS.get(source, 1.0))
    confidence_factor = 1.0
    if source in {"clip", "image", "model_guess", "vision_heuristic"}:
        confidence_factor = max(0.35, min(1.0, _safe_confidence(confidence, 0.0)))
    combined_weight = round(base_weight * confidence_factor, 4)
    weight_map[normalized] = max(weight_map.get(normalized, 0.0), combined_weight)


def _persist_detection_history(user_id, detected_list, typed_terms, recipe_ids):
    detected_ingredients = [item.get("ingredient") for item in detected_list if item.get("ingredient")]
    log_detection_history(
        user_id=user_id,
        detected_ingredients=detected_ingredients,
        typed_ingredients=typed_terms or [],
        recommended_recipe_ids=recipe_ids or [],
        selected_recipe_id=None,
    )


@upload_bp.route("/detect", methods=["POST"])
def detect_ingredient():
    try:
        if not session.get("user_id"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401

        ingredients_text = request.form.get("ingredients", "").strip()
        file = request.files.get("image")

        if not file and not ingredients_text:
            return jsonify({
                "success": False,
                "message": "Please upload an image or enter ingredients",
            }), 400

        typed_terms = []
        filename_terms = []
        ocr_terms = []
        heuristic_terms = []
        clip_terms = []
        mapped_image_terms = []
        selected_model_predictions = []
        model_error = None
        uncertain_model_only = False
        skipped_low_confidence = False
        clip_used_fallback = False

        if ingredients_text:
            typed_terms = _dedupe_keep_order(
                [token.strip() for token in ingredients_text.split(",") if token.strip()]
            )
            logger.info("[detect] typed ingredients (normalized): %s", typed_terms)

        if file and file.filename:
            upload_folder = current_app.config.get("UPLOAD_FOLDER") or os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
            )
            os.makedirs(upload_folder, exist_ok=True)

            safe_name = secure_filename(file.filename) or "uploaded_image.jpg"
            file_path = os.path.join(upload_folder, safe_name)
            file.save(file_path)

            filename_terms = _extract_filename_terms(safe_name)

            try:
                clip_detector = get_clip_detector()
                clip_started = time.perf_counter()
                clip_predictions = clip_detector.detect_ingredients(
                    file_path,
                    top_k=10,
                    min_confidence=CLIP_MIN_CONFIDENCE,
                )
                record_metric("clip_inference_time_ms", (time.perf_counter() - clip_started) * 1000.0)
            except Exception:
                clip_predictions = []

            clip_top_conf = (
                _safe_confidence(clip_predictions[0].get("confidence", 0.0))
                if clip_predictions else 0.0
            )

            if clip_predictions and clip_top_conf >= CLIP_CONFIDENT_THRESHOLD:
                clip_terms = clip_predictions
            else:
                clip_used_fallback = True
                detector = get_detector()
                raw_model_predictions = detector.detect_ingredients(file_path, top_k=5)
                selected_model_predictions = _select_model_predictions(raw_model_predictions)
                model_error = detector.model_error
                mapped_image_terms = dish_mapper.predictions_to_ingredients(
                    selected_model_predictions,
                    min_confidence=0.0,
                )
                if selected_model_predictions:
                    logger.info("[detect] dish-mapper fallback predictions: %s", selected_model_predictions)

            try:
                from app.ocr.ocr_engine import extract_ingredients_from_image

                ocr_started = time.perf_counter()
                ocr_terms = _dedupe_keep_order(extract_ingredients_from_image(file_path)[:12])
                record_metric("ocr_processing_time_ms", (time.perf_counter() - ocr_started) * 1000.0)
            except Exception:
                ocr_terms = []

            if not (typed_terms or filename_terms or ocr_terms or clip_terms or mapped_image_terms):
                heuristic_terms = _infer_visual_terms(file_path)

            top_model_conf = (
                _safe_confidence(selected_model_predictions[0].get("confidence", 0.0))
                if selected_model_predictions
                else 0.0
            )
            if (
                top_model_conf < MODEL_ONLY_MIN_CONFIDENCE
                and clip_top_conf < CLIP_CONFIDENT_THRESHOLD
                and not typed_terms
                and not filename_terms
                and not ocr_terms
                and not heuristic_terms
            ):
                uncertain_model_only = True
                mapped_image_terms = []
                skipped_low_confidence = True

        detected_store = {}
        term_weights = {}

        # Priority: typed > CLIP > OCR > filename > dish-mapped.
        for term in typed_terms:
            _merge_detected_entry(detected_store, term, "typed", 1.0)
            _add_weighted_term(term_weights, term, "typed", 1.0)

        for row in clip_terms:
            ingredient = row.get("ingredient")
            confidence = _safe_confidence(row.get("confidence", 0.0))
            _merge_detected_entry(detected_store, ingredient, "clip", confidence)
            _add_weighted_term(term_weights, ingredient, "clip", confidence)

        for term in ocr_terms:
            _merge_detected_entry(detected_store, term, "ocr", 0.70)
            _add_weighted_term(term_weights, term, "ocr", 0.70)

        for term in filename_terms:
            _merge_detected_entry(detected_store, term, "filename", 0.95)
            _add_weighted_term(term_weights, term, "filename", 0.95)

        for row in heuristic_terms:
            ingredient = row.get("ingredient")
            confidence = _safe_confidence(row.get("confidence", 0.0))
            _merge_detected_entry(detected_store, ingredient, "vision_heuristic", confidence)
            _add_weighted_term(term_weights, ingredient, "vision_heuristic", confidence)

        for row in mapped_image_terms:
            ingredient = row.get("ingredient")
            confidence = _safe_confidence(row.get("confidence", 0.0))
            source = row.get("source") or "image"
            if source == "image" and confidence < MIN_MODEL_CONFIDENCE and (typed_terms or clip_terms or ocr_terms):
                skipped_low_confidence = True
                continue
            _merge_detected_entry(detected_store, ingredient, source, confidence)
            _add_weighted_term(term_weights, ingredient, source, confidence)

        if not term_weights:
            if uncertain_model_only:
                return jsonify({
                    "success": False,
                    "message": "Please enter ingredients manually for better recommendations.",
                }), 400

            message = "No ingredients detected"
            if model_error:
                message = f"{message}. Model issue: {model_error}"
            return jsonify({"success": False, "message": message}), 400

        sorted_terms = sorted(term_weights.items(), key=lambda item: item[1], reverse=True)
        search_terms = [term for term, _ in sorted_terms]
        primary_ingredient = search_terms[0] if search_terms else ""
        logger.info("[detect] detected ingredients: %s", [item.get("ingredient") for item in detected_store.values()])
        logger.info("[detect] weighted normalized ingredients: %s", term_weights)

        recipes = recipe_service.recommend_recipes(
            query_terms=search_terms,
            limit=5,
            term_weights=term_weights,
            use_semantic=False,
        )
        if recipes:
            logger.info(
                "[detect] top recipe=%s score=%s type=%s image_source=%s",
                recipes[0].get("recipe_name") or recipes[0].get("name"),
                recipes[0].get("match_score"),
                recipes[0].get("recipe_type"),
                recipes[0].get("image_source"),
            )

        detected_list = list(detected_store.values())
        detected_list.sort(
            key=lambda row: (
                SOURCE_WEIGHTS.get(row.get("source"), 1.0),
                float(row.get("confidence", 0.0)),
            ),
            reverse=True,
        )

        recipe_ids = []
        for recipe in recipes:
            try:
                recipe_ids.append(int(recipe.get("id")))
            except Exception:
                continue

        current_user_id = session.get("user_id")
        if session.get("usage_user_id") != current_user_id:
            session["recent_recipe_ids"] = []
            session["recipes_found_count"] = 0
            session["usage_user_id"] = current_user_id

        existing_recent_ids = session.get("recent_recipe_ids") or []
        merged_recent_ids = recipe_ids + [rid for rid in existing_recent_ids if rid not in recipe_ids]
        session["recent_recipe_ids"] = merged_recent_ids[:20]
        session["recipes_found_count"] = int(session.get("recipes_found_count") or 0) + len(recipes)

        _persist_detection_history(
            user_id=current_user_id,
            detected_list=detected_list,
            typed_terms=typed_terms,
            recipe_ids=recipe_ids,
        )

        explanation = (
            "Ranking uses weighted signals: typed ingredients > CLIP image ingredients > OCR > filename > dish mapping."
        )
        if clip_used_fallback:
            explanation += " CLIP confidence was low, so dish-to-ingredient fallback was used."
        if skipped_low_confidence:
            explanation += " Low-confidence model signals were down-weighted or skipped."
        if not recipes:
            explanation += " No close recipe matches were found. Please enter ingredients manually for better recommendations."

        log_audit_event(
            user_id=session.get("user_id"),
            event_type="detect_success",
            event_payload={
                "primary_ingredient": primary_ingredient,
                "search_terms": search_terms[:8],
                "results_count": len(recipes),
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
        )

        return jsonify({
            "success": True,
            "ingredient": primary_ingredient,
            "detected": detected_list,
            "search_terms": search_terms,
            "explanation": explanation,
            "recipes": recipes or [],
        })
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500

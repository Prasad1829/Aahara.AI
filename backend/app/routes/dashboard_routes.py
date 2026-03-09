import json

from flask import Blueprint, jsonify, session

from app.services.recipe_service import get_recipe_service
from app.utils.db_utils import (
    get_saved_recipes_count,
    get_user_favorite_recipes,
    get_user_favorites_count,
    get_user_recipes,
    get_user_tried_recipes_count,
)


dashboard_bp = Blueprint("dashboard", __name__)

recipe_service = get_recipe_service()


def _require_session():
    if not session.get("user_id"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    return None


def _parse_ingredients(value):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value or "").strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except Exception:
        pass
    return [item.strip() for item in text.split(",") if item.strip()]


def _rows_to_recipe_cards(rows, limit=8):
    cards = []
    for row in rows or []:
        source_id = row.get("source_recipe_id")
        recipe = None
        if source_id not in (None, ""):
            try:
                recipe = recipe_service.get_recipe_by_id(int(source_id))
            except Exception:
                recipe = None
        if not recipe:
            recipe = {
                "id": source_id if source_id not in (None, "") else None,
                "name": row.get("recipe_name") or "Saved Recipe",
                "ingredients": _parse_ingredients(row.get("ingredients")),
                "image_url": None,
            }
        cards.append(recipe)
        if len(cards) >= limit:
            break
    return cards


def _recent_session_recipes(limit=8):
    recent_ids = session.get("recent_recipe_ids") or []
    cards = []
    for recipe_id in recent_ids:
        try:
            recipe = recipe_service.get_recipe_by_id(int(recipe_id))
        except Exception:
            recipe = None
        if recipe:
            cards.append(recipe)
        if len(cards) >= limit:
            break
    return cards


@dashboard_bp.route("", methods=["GET"])
@dashboard_bp.route("/", methods=["GET"])
def dashboard_summary():
    unauthorized = _require_session()
    if unauthorized:
        return unauthorized
    try:
        user_id = session.get("user_id")
        saved_rows = get_user_recipes(user_id, limit=8)
        favorite_rows = get_user_favorite_recipes(user_id, limit=8)

        recent_recipes = _recent_session_recipes(limit=8)
        saved_recipes = _rows_to_recipe_cards(favorite_rows or saved_rows, limit=8)

        return jsonify({
            "success": True,
            "stats": {
                "total_recipes": int(session.get("recipes_found_count") or 0),
                "saved_count": int(get_saved_recipes_count(user_id) or 0),
                "tried_count": int(get_user_tried_recipes_count(user_id) or 0),
                "favorite_count": int(get_user_favorites_count(user_id) or 0),
            },
            "recent_recipes": recent_recipes,
            "saved_recipes": saved_recipes,
            "saved_history": _rows_to_recipe_cards(saved_rows, limit=8),
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e),
        }), 500


# USER DASHBOARD INFO
@dashboard_bp.route("/info", methods=["GET"])
def dashboard_info():
    unauthorized = _require_session()
    if unauthorized:
        return unauthorized
    try:
        return jsonify({
            "success": True,
            "user": {
                "id": session.get("user_id"),
                "name": session.get("user_name"),
                "email": session.get("user_email"),
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e),
        }), 500


# DASHBOARD STATS
@dashboard_bp.route("/stats", methods=["GET"])
def dashboard_stats():
    unauthorized = _require_session()
    if unauthorized:
        return unauthorized
    try:
        user_id = session.get("user_id")
        total_recipes = int(session.get("recipes_found_count") or 0)

        return jsonify({
            "success": True,
            "stats": {
                "total_recipes": total_recipes,
                "saved_count": int(get_saved_recipes_count(user_id) or 0),
                "tried_count": int(get_user_tried_recipes_count(user_id) or 0),
                "favorite_count": int(get_user_favorites_count(user_id) or 0),
                "user": session.get("user_name"),
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e),
        }), 500

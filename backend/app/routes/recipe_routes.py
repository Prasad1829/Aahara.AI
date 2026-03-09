import json

from flask import Blueprint, jsonify, request, session

from app.services.recipe_service import get_recipe_service
from app.utils.db_utils import (
    _table_has_column,
    execute_commit,
    execute_query,
    get_user_recipes,
    log_audit_event,
    save_recipe,
    update_latest_detection_selected_recipe,
)


recipe_bp = Blueprint("recipe", __name__)
recipe_service = get_recipe_service()


def _unauthorized_if_needed():
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


def _saved_rows_to_recipes(rows):
    recipes = []
    for row in rows or []:
        source_recipe_id = row.get("source_recipe_id")
        recipe = None
        if source_recipe_id not in (None, ""):
            try:
                recipe = recipe_service.get_recipe_by_id(int(source_recipe_id))
            except Exception:
                recipe = None
        if not recipe:
            recipe = {
                "id": source_recipe_id if source_recipe_id not in (None, "") else row.get("id"),
                "name": row.get("recipe_name") or "Saved Recipe",
                "ingredients": _parse_ingredients(row.get("ingredients")),
                "instructions": [],
                "image_url": None,
            }
        recipe = dict(recipe)
        recipe["saved_id"] = row.get("id")
        recipe["source_recipe_id"] = source_recipe_id
        recipe["is_favorite"] = int(row.get("is_favorite") or 0)
        recipe["tried"] = int(row.get("tried") or 0)
        recipes.append(recipe)
    return recipes


@recipe_bp.route("/all", methods=["GET"])
def get_all_recipes():
    unauthorized = _unauthorized_if_needed()
    if unauthorized:
        return unauthorized
    try:
        user_id = session.get("user_id")
        rows = get_user_recipes(user_id, limit=200)
        recipes = _saved_rows_to_recipes(rows)
        return jsonify({"success": True, "recipes": recipes})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@recipe_bp.route("/save", methods=["POST"])
def save_recipe_for_user():
    unauthorized = _unauthorized_if_needed()
    if unauthorized:
        return unauthorized
    try:
        payload = request.get_json(silent=True) or {}
        raw_recipe_id = payload.get("recipe_id")
        if raw_recipe_id in (None, ""):
            return jsonify({"success": False, "message": "recipe_id is required"}), 400

        try:
            recipe_id = int(raw_recipe_id)
        except Exception:
            return jsonify({"success": False, "message": "Invalid recipe_id"}), 400

        recipe = recipe_service.get_recipe_by_id(recipe_id)
        if not recipe:
            return jsonify({"success": False, "message": "Recipe not found"}), 404

        user_id = session.get("user_id")
        if _table_has_column("saved_recipes", "source_recipe_id"):
            duplicate = execute_query(
                "SELECT id FROM saved_recipes WHERE user_id = %s AND source_recipe_id = %s LIMIT 1",
                (user_id, recipe_id),
            )
        else:
            duplicate = execute_query(
                "SELECT id FROM saved_recipes WHERE user_id = %s AND recipe_name = %s LIMIT 1",
                (user_id, recipe.get("name") or f"Recipe {recipe_id}"),
            )
        if duplicate:
            return jsonify({"success": True, "message": "Recipe already saved"})

        saved = save_recipe(
            user_id=user_id,
            recipe_name=recipe.get("name") or f"Recipe {recipe_id}",
            ingredients=json.dumps(recipe.get("ingredients", []), ensure_ascii=False),
            source_recipe_id=recipe_id,
        )
        if not saved:
            return jsonify({"success": False, "message": "Could not save recipe"}), 500

        update_latest_detection_selected_recipe(user_id=user_id, selected_recipe_id=recipe_id)

        log_audit_event(
            user_id=user_id,
            event_type="save_recipe",
            event_payload={"recipe_id": recipe_id, "recipe_name": recipe.get("name")},
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
        )

        return jsonify({"success": True, "message": "Recipe saved"})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@recipe_bp.route("/ingredient/<ingredient>", methods=["GET"])
def get_by_ingredient(ingredient):
    unauthorized = _unauthorized_if_needed()
    if unauthorized:
        return unauthorized
    try:
        recipes = recipe_service.get_recipes_by_ingredient(ingredient)
        return jsonify({
            "success": True,
            "ingredient": ingredient,
            "recipes": recipes,
        })
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@recipe_bp.route("/<int:recipe_id>", methods=["GET"])
def get_recipe(recipe_id):
    unauthorized = _unauthorized_if_needed()
    if unauthorized:
        return unauthorized
    try:
        recipe = recipe_service.get_recipe_by_id(recipe_id)
        if recipe:
            return jsonify({"success": True, "recipe": recipe})
        return jsonify({"success": False, "message": "Recipe not found"}), 404
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@recipe_bp.route("/<int:recipe_id>/unsave", methods=["POST"])
def unsave_recipe(recipe_id):
    unauthorized = _unauthorized_if_needed()
    if unauthorized:
        return unauthorized
    try:
        user_id = session.get("user_id")
        if _table_has_column("saved_recipes", "source_recipe_id"):
            deleted = execute_commit(
                """
                DELETE FROM saved_recipes
                WHERE user_id = %s
                  AND (source_recipe_id = %s OR id = %s)
                """,
                (user_id, recipe_id, recipe_id),
            )
        else:
            deleted = execute_commit(
                "DELETE FROM saved_recipes WHERE user_id = %s AND id = %s",
                (user_id, recipe_id),
            )
        if not deleted:
            return jsonify({"success": False, "message": "Could not remove recipe"}), 500
        log_audit_event(
            user_id=user_id,
            event_type="unsave_recipe",
            event_payload={"recipe_id": recipe_id},
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
        )
        return jsonify({"success": True, "message": "Recipe removed"})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500

from flask import Blueprint, jsonify, request, session

from app.services.ingredient_suggester import get_ingredient_suggester


ingredient_bp = Blueprint("ingredient", __name__)
ingredient_suggester = get_ingredient_suggester()


def _unauthorized_if_needed():
    if not session.get("user_id"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    return None


@ingredient_bp.route("/suggestions", methods=["GET"])
def ingredient_suggestions():
    unauthorized = _unauthorized_if_needed()
    if unauthorized:
        return unauthorized

    raw_ingredient = request.args.get("ingredient", "")
    ingredient = str(raw_ingredient or "").strip()
    if not ingredient:
        return jsonify({"success": False, "message": "ingredient query parameter is required"}), 400

    raw_limit = request.args.get("limit", "10")
    try:
        limit = max(1, min(int(raw_limit), 25))
    except Exception:
        limit = 10

    suggestions = ingredient_suggester.suggest(ingredient, limit=limit)
    return jsonify({
        "success": True,
        "ingredient": ingredient,
        "suggestions": suggestions,
    })

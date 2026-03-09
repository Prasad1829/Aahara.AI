from flask import Blueprint, jsonify, request, session

from app.ml.image_validator import get_image_validator
from app.ml.ingredient_detector import get_detector
from app.services.recipe_image_service import get_recipe_image_service
from app.services.recipe_service import get_recipe_service
from app.utils.system_metrics import get_metrics_snapshot
from app.utils.db_utils import (
    delete_user_account,
    get_admin_overview_data,
    get_all_users_admin,
    get_ingredient_analytics_data,
    get_user_by_id,
    log_audit_event,
    set_user_role,
    set_user_status,
)


admin_bp = Blueprint("admin", __name__)


def _is_admin_role(role):
    return role in {"admin", "super_admin"}


def _require_admin():
    if not session.get("user_id"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    if not _is_admin_role(session.get("user_role", "user")):
        return jsonify({"success": False, "message": "Forbidden"}), 403
    return None


@admin_bp.route("/overview", methods=["GET"])
def admin_overview():
    unauthorized = _require_admin()
    if unauthorized:
        return unauthorized
    try:
        data = get_admin_overview_data(days=7)
        return jsonify({"success": True, **data})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@admin_bp.route("/users", methods=["GET"])
def admin_users():
    unauthorized = _require_admin()
    if unauthorized:
        return unauthorized
    try:
        users = get_all_users_admin(limit=1000)
        return jsonify({"success": True, "users": users})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@admin_bp.route("/ingredient-analytics", methods=["GET"])
def admin_ingredient_analytics():
    unauthorized = _require_admin()
    if unauthorized:
        return unauthorized
    try:
        raw_days = request.args.get("days", "30")
        try:
            days = max(1, min(int(raw_days), 365))
        except Exception:
            days = 30
        data = get_ingredient_analytics_data(days=days)
        return jsonify({"success": True, "days": days, **data})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@admin_bp.route("/system-metrics", methods=["GET"])
def admin_system_metrics():
    unauthorized = _require_admin()
    if unauthorized:
        return unauthorized
    try:
        metrics = get_metrics_snapshot()
        return jsonify({"success": True, "metrics": metrics})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@admin_bp.route("/system-status", methods=["GET"])
def admin_system_status():
    unauthorized = _require_admin()
    if unauthorized:
        return unauthorized
    try:
        recipe_service = get_recipe_service()
        image_service = get_recipe_image_service()
        yolo_detector = get_detector()
        clip_validator = get_image_validator()

        payload = {
            "image_fetch_enabled": bool(image_service.fetch_enabled),
            "active_image_provider": image_service.provider or "auto",
            "embedding_model_loaded": bool(recipe_service.embedding_model_loaded()),
            "clip_model_loaded": bool(clip_validator.loaded),
            "yolo_model_loaded": bool(yolo_detector.loaded),
        }
        return jsonify({"success": True, **payload})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@admin_bp.route("/users/<int:target_user_id>/status", methods=["POST"])
def admin_set_user_status(target_user_id):
    unauthorized = _require_admin()
    if unauthorized:
        return unauthorized
    try:
        payload = request.get_json(silent=True) or {}
        status = str(payload.get("status", "")).strip().lower()
        if status not in {"active", "inactive"}:
            return jsonify({"success": False, "message": "Status must be active or inactive"}), 400

        current_user_id = int(session.get("user_id"))
        if target_user_id == current_user_id and status != "active":
            return jsonify({"success": False, "message": "You cannot deactivate your own account"}), 400

        target_user = get_user_by_id(target_user_id)
        if not target_user:
            return jsonify({"success": False, "message": "User not found"}), 404

        if target_user.get("role") == "super_admin" and session.get("user_role") != "super_admin":
            return jsonify({"success": False, "message": "Only super admin can manage super admin accounts"}), 403

        ok = set_user_status(target_user_id, status)
        if not ok:
            return jsonify({"success": False, "message": "Failed to update user status"}), 500

        log_audit_event(
            user_id=current_user_id,
            event_type="admin_set_status",
            event_payload={"target_user_id": target_user_id, "new_status": status},
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
        )
        return jsonify({"success": True, "message": "User status updated"})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@admin_bp.route("/users/<int:target_user_id>/role", methods=["POST"])
def admin_set_user_role(target_user_id):
    unauthorized = _require_admin()
    if unauthorized:
        return unauthorized
    try:
        payload = request.get_json(silent=True) or {}
        role = str(payload.get("role", "")).strip().lower()
        if role not in {"user", "admin", "super_admin"}:
            return jsonify({"success": False, "message": "Invalid role"}), 400

        current_user_id = int(session.get("user_id"))
        current_role = session.get("user_role", "user")

        target_user = get_user_by_id(target_user_id)
        if not target_user:
            return jsonify({"success": False, "message": "User not found"}), 404

        target_role = target_user.get("role", "user")
        if current_role != "super_admin" and (role == "super_admin" or target_role == "super_admin"):
            return jsonify({"success": False, "message": "Only super admin can assign/manage super admin role"}), 403

        if target_user_id == current_user_id and role != current_role:
            return jsonify({"success": False, "message": "You cannot change your own role"}), 400

        ok = set_user_role(target_user_id, role)
        if not ok:
            return jsonify({"success": False, "message": "Failed to update user role"}), 500

        log_audit_event(
            user_id=current_user_id,
            event_type="admin_set_role",
            event_payload={"target_user_id": target_user_id, "new_role": role},
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
        )
        return jsonify({"success": True, "message": "User role updated"})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@admin_bp.route("/users/<int:target_user_id>", methods=["DELETE"])
def admin_delete_user(target_user_id):
    unauthorized = _require_admin()
    if unauthorized:
        return unauthorized
    try:
        current_user_id = int(session.get("user_id"))
        current_role = session.get("user_role", "user")

        if target_user_id == current_user_id:
            return jsonify({"success": False, "message": "You cannot delete your own account"}), 400

        target_user = get_user_by_id(target_user_id)
        if not target_user:
            return jsonify({"success": False, "message": "User not found"}), 404

        if target_user.get("role") == "super_admin" and current_role != "super_admin":
            return jsonify({"success": False, "message": "Only super admin can delete super admin accounts"}), 403

        ok = delete_user_account(target_user_id)
        if not ok:
            return jsonify({"success": False, "message": "Failed to delete user"}), 500

        log_audit_event(
            user_id=current_user_id,
            event_type="admin_delete_user",
            event_payload={"target_user_id": target_user_id, "target_email": target_user.get("email")},
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
        )
        return jsonify({"success": True, "message": "User deleted"})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500

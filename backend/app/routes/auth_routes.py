from flask import Blueprint, current_app, jsonify, request, session

from app.services.auth_service import AuthService
from app.utils.api_response import error_response, success_response
from app.utils.db_utils import (
    execute_commit,
    get_user_by_email,
    get_user_by_id,
    log_audit_event,
    update_user_last_login,
)
from app.utils.rate_limit import SlidingWindowRateLimiter


auth_bp = Blueprint("auth", __name__)
_login_rate_limiter = None
_login_rate_limiter_config = None


def _client_ip():
    forwarded = str(request.headers.get("X-Forwarded-For", "")).strip()
    if forwarded:
        return forwarded.split(",")[0].strip() or "unknown"
    return str(request.remote_addr or "unknown").strip() or "unknown"


def _get_login_rate_limiter():
    global _login_rate_limiter, _login_rate_limiter_config
    attempts = int(current_app.config.get("LOGIN_RATE_LIMIT_ATTEMPTS", 5))
    window_seconds = int(current_app.config.get("LOGIN_RATE_LIMIT_WINDOW_SECONDS", 60))
    config_tuple = (attempts, window_seconds)
    if _login_rate_limiter is None or _login_rate_limiter_config != config_tuple:
        _login_rate_limiter = SlidingWindowRateLimiter(
            max_attempts=attempts,
            window_seconds=window_seconds,
        )
        _login_rate_limiter_config = config_tuple
    return _login_rate_limiter


@auth_bp.route("/csrf", methods=["GET"])
def csrf_token():
    return success_response(
        data={"csrf_token": session.get("csrf_token", "")},
        csrf_token=session.get("csrf_token", ""),
    )


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    result = AuthService.register_user(name, email, password)
    if result.get("success"):
        user = get_user_by_email(email)
        log_audit_event(
            user_id=(user or {}).get("id"),
            event_type="register_success",
            event_payload={"email": email},
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
        )
    return jsonify(result)


@auth_bp.route("/login", methods=["POST"])
def login():
    limiter = _get_login_rate_limiter()
    ip_address = _client_ip()
    if not limiter.allow(ip_address):
        return error_response(
            error="Too many login attempts. Please try again in a minute.",
            status=429,
        )

    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    result = AuthService.login_user(email, password)
    if result.get("success") and result.get("user"):
        user = result["user"]
        previous_usage_user = session.get("usage_user_id")
        session["user_id"] = user.get("id")
        session["user_name"] = user.get("name")
        session["user_email"] = user.get("email")
        session["user_role"] = user.get("role", "user")
        session["user_status"] = user.get("status", "active")
        session["user_created_at"] = user.get("created_at")
        if previous_usage_user != user.get("id"):
            session["recent_recipe_ids"] = []
            session["recipes_found_count"] = 0
        session["usage_user_id"] = user.get("id")
        update_user_last_login(user.get("id"))
        log_audit_event(
            user_id=user.get("id"),
            event_type="login_success",
            event_payload={"email": user.get("email"), "role": user.get("role", "user")},
            ip_address=ip_address,
            user_agent=request.headers.get("User-Agent"),
        )
        result["message"] = "Login successful"

    return jsonify(result)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    user_id = session.get("user_id")
    if user_id:
        log_audit_event(
            user_id=user_id,
            event_type="logout",
            event_payload={"email": session.get("user_email")},
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
        )
    session.clear()
    return success_response(message="Logged out")


@auth_bp.route("/me", methods=["GET"])
def me():
    user_id = session.get("user_id")
    if not user_id:
        return error_response(error="Unauthorized", status=401)

    user = get_user_by_id(user_id)
    if user:
        session["user_name"] = user.get("name")
        session["user_email"] = user.get("email")
        session["user_role"] = user.get("role", "user")
        session["user_status"] = user.get("status", "active")
        session["user_created_at"] = user.get("created_at")

    user_payload = {
        "id": user_id,
        "name": session.get("user_name"),
        "email": session.get("user_email"),
        "role": session.get("user_role", "user"),
        "status": session.get("user_status", "active"),
        "created_at": session.get("user_created_at"),
    }
    return success_response(data={"user": user_payload}, user=user_payload)


@auth_bp.route("/profile", methods=["POST"])
def update_profile():
    user_id = session.get("user_id")
    if not user_id:
        return error_response(error="Unauthorized", status=401)

    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()

    if not name or not email:
        return error_response(error="Name and email are required", status=400)
    if "@" not in email or "." not in email.split("@")[-1]:
        return error_response(error="Enter a valid email address", status=400)

    existing = get_user_by_email(email)
    if existing and int(existing.get("id", 0)) != int(user_id):
        return error_response(error="Email already in use", status=409)

    updated = execute_commit(
        "UPDATE users SET name = %s, email = %s WHERE id = %s",
        (name, email, user_id),
    )
    if not updated:
        return error_response(error="Could not update profile", status=500)

    refreshed = get_user_by_id(user_id) or {}
    session["user_name"] = refreshed.get("name", name)
    session["user_email"] = refreshed.get("email", email)
    session["user_role"] = refreshed.get("role", session.get("user_role", "user"))
    session["user_status"] = refreshed.get("status", session.get("user_status", "active"))
    session["user_created_at"] = refreshed.get("created_at", session.get("user_created_at"))

    log_audit_event(
        user_id=user_id,
        event_type="profile_update",
        event_payload={"name": session.get("user_name"), "email": session.get("user_email")},
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
    )

    user_payload = {
        "id": user_id,
        "name": session.get("user_name"),
        "email": session.get("user_email"),
        "role": session.get("user_role", "user"),
        "status": session.get("user_status", "active"),
        "created_at": session.get("user_created_at"),
    }
    return success_response(
        message="Profile updated",
        data={"user": user_payload},
        user=user_payload,
    )

import json
import os
import secrets
import sys

from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.config import DevelopmentConfig, ProductionConfig, TestingConfig
from app.extensions import bcrypt, db, migrate
from app.routes.admin_routes import admin_bp
from app.routes.auth_routes import auth_bp
from app.routes.dashboard_routes import dashboard_bp
from app.routes.ingredient_routes import ingredient_bp
from app.routes.recipe_routes import recipe_bp
from app.services.recipe_service import get_recipe_service
from app.utils.api_response import normalize_payload_for_api
from app.utils.db_utils import init_db


jwt = JWTManager()

_CONFIG_MAP = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}

_CSRF_PROTECTED_PREFIXES = (
    "/api/auth/",
    "/api/recipes/",
    "/api/admin/",
)


def _resolve_config(config_name):
    selected = str(config_name or os.getenv("FLASK_CONFIG", "development")).strip().lower()
    return _CONFIG_MAP.get(selected, DevelopmentConfig)


def _should_require_csrf(path):
    clean_path = str(path or "")
    return any(clean_path.startswith(prefix) for prefix in _CSRF_PROTECTED_PREFIXES)


def create_app(config_name=None, config_overrides=None):
    app = Flask(
        __name__,
        template_folder=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../frontend/templates")
        ),
        static_folder=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../frontend/static")
        ),
        static_url_path="/static",
    )

    app.config.from_object(_resolve_config(config_name))
    if config_overrides:
        app.config.update(config_overrides)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY must be provided via environment variables.")
    if not app.config.get("JWT_SECRET_KEY"):
        app.config["JWT_SECRET_KEY"] = app.config.get("SECRET_KEY")

    upload_folder = app.config.get("UPLOAD_FOLDER")
    if upload_folder:
        os.makedirs(upload_folder, exist_ok=True)

    CORS(app, supports_credentials=True)
    jwt.init_app(app)
    bcrypt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # Import model metadata so Flask-Migrate detects all tables.
    from app import models  # noqa: F401

    if app.config.get("AUTO_INIT_DB"):
        try:
            init_db(app)
            print("[OK] Database initialized successfully")
        except Exception as exc:
            print(f"[!] Database initialization warning: {exc}")

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(ingredient_bp, url_prefix="/api/ingredients")
    app.register_blueprint(recipe_bp, url_prefix="/api/recipes")

    from app.routes.upload_routes import upload_bp

    app.register_blueprint(upload_bp, url_prefix="/api")

    @app.before_request
    def csrf_guard():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(32)

        if not app.config.get("API_CSRF_ENABLED", True):
            return None

        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return None

        if not _should_require_csrf(request.path):
            return None

        token = (
            request.headers.get("X-CSRF-Token")
            or request.headers.get("X-CSRFToken")
            or ""
        )
        if token and token == session.get("csrf_token"):
            return None

        return jsonify(
            {
                "success": False,
                "error": "CSRF token missing or invalid",
                "message": "CSRF token missing or invalid",
            }
        ), 403

    @app.after_request
    def normalize_api_response(response):
        if not str(request.path or "").startswith("/api/"):
            return response
        if not response.is_json:
            return response

        payload = response.get_json(silent=True)
        normalized = normalize_payload_for_api(payload, response.status_code)
        if normalized == payload:
            return response

        response.set_data(json.dumps(normalized, ensure_ascii=False))
        response.headers["Content-Type"] = "application/json"
        return response

    should_warmup = bool(app.config.get("RECIPE_SERVICE_WARMUP", True))
    argv_tokens = {str(arg).strip().lower() for arg in sys.argv[1:]}
    if "db" in argv_tokens:
        should_warmup = False

    # Warm up singleton recipe service once during startup for caching/indexing.
    if should_warmup:
        try:
            get_recipe_service()
        except Exception as exc:
            print(f"[!] Recipe service warmup warning: {exc}")

    return app

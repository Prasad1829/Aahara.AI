import os
from urllib.parse import quote_plus

from dotenv import load_dotenv


load_dotenv()


def _env_int(name, default):
    raw_value = os.getenv(name, str(default))
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        return int(default)


def _build_sqlalchemy_uri():
    explicit_uri = str(os.getenv("SQLALCHEMY_DATABASE_URI", "")).strip()
    if explicit_uri:
        return explicit_uri

    host = os.getenv("DB_HOST", "localhost")
    port = _env_int("DB_PORT", 3306)
    user = os.getenv("DB_USER", "root")
    password = quote_plus(os.getenv("DB_PASSWORD", ""))
    database = os.getenv("DB_NAME", "ingredient_recipe_ai")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = _env_int("DB_PORT", 3306)
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "ingredient_recipe_ai")
    OWNER_ADMIN_EMAIL = os.getenv("OWNER_ADMIN_EMAIL", "owner@example.com")

    UPLOAD_FOLDER = os.path.abspath(
        os.getenv(
            "UPLOAD_FOLDER",
            os.path.join(os.path.dirname(__file__), "..", "..", "uploads"),
        )
    )

    SQLALCHEMY_DATABASE_URI = _build_sqlalchemy_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RECIPE_IMAGE_FETCH_ENABLED = str(os.getenv("RECIPE_IMAGE_FETCH_ENABLED", "1")).strip()
    RECIPE_IMAGE_PROVIDER = str(os.getenv("RECIPE_IMAGE_PROVIDER", "auto")).strip().lower()

    API_CSRF_ENABLED = str(os.getenv("API_CSRF_ENABLED", "1")).strip() != "0"
    LOGIN_RATE_LIMIT_ATTEMPTS = _env_int("LOGIN_RATE_LIMIT_ATTEMPTS", 5)
    LOGIN_RATE_LIMIT_WINDOW_SECONDS = _env_int("LOGIN_RATE_LIMIT_WINDOW_SECONDS", 60)
    AUTO_INIT_DB = str(os.getenv("AUTO_INIT_DB", "0")).strip() != "0"
    RECIPE_SERVICE_WARMUP = str(os.getenv("RECIPE_SERVICE_WARMUP", "1")).strip() != "0"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV = "development"


class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV = "production"
    SESSION_COOKIE_SECURE = str(os.getenv("SESSION_COOKIE_SECURE", "1")).strip() != "0"


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = False
    ENV = "testing"
    API_CSRF_ENABLED = False
    LOGIN_RATE_LIMIT_ATTEMPTS = 999999
    RECIPE_SERVICE_WARMUP = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = os.getenv("SECRET_KEY", "test-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "test-jwt-secret-key")

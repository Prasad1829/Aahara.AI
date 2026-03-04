import os


def get_env(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value.strip()


DATABASE_URL = get_env("DATABASE_URL", "sqlite:///./recipe.db")
SECRET_KEY = get_env("SECRET_KEY", "dev_only_change_me")
ALGORITHM = get_env("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(get_env("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
TESSERACT_CMD = get_env("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")

CORS_ORIGINS = [
    origin.strip()
    for origin in get_env("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]

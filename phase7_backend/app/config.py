import os


def get_env(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value.strip()


mongodb_env = os.getenv("MONGODB_URL")
if not mongodb_env or not mongodb_env.strip():
    database_env = os.getenv("DATABASE_URL")
    if database_env and database_env.strip().startswith("mongodb"):
        MONGODB_URL = database_env.strip()
    else:
        MONGODB_URL = "mongodb+srv://prasad10052004_db_user:cQB5GIq5x4ASOm3J@cluster0.ejqcczp.mongodb.net/aahara_ai?appName=Cluster0"
else:
    MONGODB_URL = mongodb_env.strip()

DATABASE_URL = MONGODB_URL
SECRET_KEY = get_env("SECRET_KEY", "85b3bc224fb0ecf8c92a95c9a419be226e6328329de400dbb4dc80bf61b474bb")
ALGORITHM = get_env("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(get_env("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
TESSERACT_CMD = get_env("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")

CORS_ORIGINS = [
    origin.strip()
    for origin in get_env(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,https://aahara-ai-one.vercel.app,https://aahara-ai.vercel.app,https://aahara-ai-main-team-prasad2.vercel.app",
    ).split(",")
    if origin.strip()
]
GOOGLE_CLIENT_ID = get_env("GOOGLE_CLIENT_ID", "")
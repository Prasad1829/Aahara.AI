from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app import models
from app.config import CORS_ORIGINS
from app.database import SessionLocal, engine
from app.models import Ingredient, Recipe
from app.routes import auth, upload, instructions, wishlist, history
from app.services.recipe_import import import_regional_recipes
from recipes_data import recipes_data

models.Base.metadata.create_all(bind=engine)


def ensure_recipe_columns():
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    if "recipes" not in table_names:
        return

    columns = {column["name"] for column in inspector.get_columns("recipes")}
    with engine.begin() as conn:
        if "cooking_time_minutes" not in columns:
            conn.execute(text("ALTER TABLE recipes ADD COLUMN cooking_time_minutes INTEGER DEFAULT 30 NOT NULL"))
        if "instructions" not in columns:
            conn.execute(text("ALTER TABLE recipes ADD COLUMN instructions TEXT DEFAULT '' NOT NULL"))
        if "image_url" not in columns:
            conn.execute(text("ALTER TABLE recipes ADD COLUMN image_url TEXT"))


def ensure_user_columns():
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    if "users" not in table_names:
        return

    columns = {column["name"] for column in inspector.get_columns("users")}
    with engine.begin() as conn:
        if "full_name" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR"))
        if "phone_number" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN phone_number VARCHAR"))
        if "avatar_url" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR"))
        if "auth_provider" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN auth_provider VARCHAR"))
        if "provider_subject" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN provider_subject VARCHAR"))


def seed_default_recipes():
    db = SessionLocal()
    try:
        ingredient_cache = {}

        for recipe_data in recipes_data:
            existing_recipe = db.query(Recipe).filter(Recipe.name == recipe_data["name"]).first()
            if existing_recipe is None:
                recipe = Recipe(name=recipe_data["name"])
                db.add(recipe)
            else:
                recipe = existing_recipe

            recipe.is_veg = recipe_data.get("is_veg", True)
            recipe.cooking_time_minutes = recipe_data.get("cooking_time_minutes", 30)
            recipe.instructions = recipe_data.get("instructions", "")

            recipe.ingredients.clear()

            for ing_name in recipe_data.get("ingredients", []):
                normalized = ing_name.lower().strip()
                ingredient = ingredient_cache.get(normalized)

                if ingredient is None:
                    ingredient = db.query(Ingredient).filter(Ingredient.name == normalized).first()
                    if ingredient is None:
                        ingredient = Ingredient(name=normalized)
                        db.add(ingredient)
                        db.flush()
                    ingredient_cache[normalized] = ingredient

                recipe.ingredients.append(ingredient)

        db.commit()
    finally:
        db.close()


app = FastAPI(title="Ingredient Based Intelligent Recipe Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.on_event("startup")
def startup_event():
    ensure_recipe_columns()
    ensure_user_columns()
    seed_default_recipes()
    import_regional_recipes()


uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


app.include_router(auth.router)
app.include_router(upload.router, tags=["upload"])
app.include_router(instructions.router, tags=["instructions"])
app.include_router(wishlist.router, tags=["wishlist"])
app.include_router(history.router, tags=["history"])

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.config import CORS_ORIGINS
from app.database import SessionLocal
from app.models import Ingredient, Recipe
from app.routes import auth, upload, instructions, wishlist, history
from recipes_data import recipes_data


def seed_default_recipes():
    db = SessionLocal()
    try:
        for recipe_data in recipes_data:
            existing_recipe = db.query(Recipe).filter(Recipe.name == recipe_data["name"]).first()
            if existing_recipe is None:
                ing_objs = [Ingredient(name=ing.lower().strip()) for ing in recipe_data.get("ingredients", [])]
                recipe = Recipe(
                    name=recipe_data["name"],
                    is_veg=recipe_data.get("is_veg", True),
                    cooking_time_minutes=recipe_data.get("cooking_time_minutes", 30),
                    instructions=recipe_data.get("instructions", ""),
                    ingredients=ing_objs,
                )
                db.add(recipe)
        db.commit()
    finally:
        db.close()


app = FastAPI(title="Ingredient Based Intelligent Recipe Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "message": "Aahara.AI API is running (MongoDB Atlas)", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "ok", "database": "mongodb"}


@app.on_event("startup")
def startup_event():
    seed_default_recipes()


uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


app.include_router(auth.router)
app.include_router(upload.router, tags=["upload"])
app.include_router(instructions.router, tags=["instructions"])
app.include_router(wishlist.router, tags=["wishlist"])
app.include_router(history.router, tags=["history"])

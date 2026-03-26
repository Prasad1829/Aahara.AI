from app.database import SessionLocal, engine
from app import models
from app.models import Recipe, Ingredient
from recipes_data import recipes_data

# Create tables if not exist
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

def get_or_create_ingredient(name):
    ingredient = db.query(Ingredient).filter(Ingredient.name == name).first()
    if not ingredient:
        ingredient = Ingredient(name=name)
        db.add(ingredient)
        db.commit()
        db.refresh(ingredient)
    return ingredient

for recipe_data in recipes_data:
    # Prevent duplicate recipes
    existing = db.query(Recipe).filter(Recipe.name == recipe_data["name"]).first()
    if existing:
        continue

    recipe = Recipe(
        name=recipe_data["name"],
        is_veg=recipe_data["is_veg"]
    )

    for ing_name in recipe_data["ingredients"]:
        ing = get_or_create_ingredient(ing_name.lower().strip())
        recipe.ingredients.append(ing)

    db.add(recipe)

db.commit()
print("Recipes inserted successfully")
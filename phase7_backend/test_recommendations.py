from app.database import SessionLocal
from app.models import Recipe
from app.services.recommendation_service import get_recipe_recommendations
import json

print("TESTING: What recommendations does API return for [chicken, tomato, onion]?")
print("=" * 70)

result = get_recipe_recommendations(['chicken', 'tomato', 'onion'])

print(f"\n✓ RECOMMENDED RECIPES: {len(result['recommended_recipes'])} found")
for i, recipe in enumerate(result['recommended_recipes'][:10], 1):
    print(f"  {i}. {recipe['name']} (score: {recipe['match_score']})")
    print(f"     Matched: {recipe['matched_ingredients']}, Missing: {recipe['missing_ingredients']}")

print(f"\n✓ ADDITIONAL RECIPES: {len(result['additional_recipes'])} found")
for i, recipe in enumerate(result['additional_recipes'][:5], 1):
    print(f"  {i}. {recipe['name']} (score: {recipe['match_score']})")

# Check if Chicken Curry exists in DB
db = SessionLocal()
chicken_curry = db.query(Recipe).filter(Recipe.name == "Chicken Curry").first()
if chicken_curry:
    print(f"\n✓ Chicken Curry EXISTS in database")
    ing_dict = json.loads(chicken_curry.ingredients_json)
    print(f"  Main ingredients: {ing_dict.get('main', [])}")
else:
    print(f"\n✗ Chicken Curry NOT FOUND in database")
db.close()

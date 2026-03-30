import json
from app.database import SessionLocal
from app.models import Recipe
from app.services.recommendation_service import get_recipe_recommendations

db = SessionLocal()

# Test 1: Get recommendations for chicken curry ingredients
print("TEST 1: Recommendations for ['chicken', 'tomato', 'onion']")
print("=" * 60)
results = get_recipe_recommendations(['chicken', 'tomato', 'onion'])

if results['recommended_recipes']:
    recipe = results['recommended_recipes'][0]
    print(f"\nTop Recipe: {recipe['name']}")
    print(f"Match Score: {recipe['match_score']}")
    print(f"Has grouped ingredients: {'ingredients_grouped' in recipe}")
    
    if 'ingredients_grouped' in recipe and recipe['ingredients_grouped']:
        print(f"Grouped Structure:")
        for group, items in recipe['ingredients_grouped'].items():
            print(f"  {group}: {items}")
else:
    print("No recommendations found")

# Test 2: Verify JSON is being parsed correctly
print("\n\nTEST 2: Direct Database Query")
print("=" * 60)
recipe = db.query(Recipe).filter(Recipe.name == "Aloo Gobi").first()
if recipe:
    print(f"Recipe: {recipe.name}")
    print(f"JSON Stored: {recipe.ingredients_json}")
    if recipe.ingredients_json:
        parsed = json.loads(recipe.ingredients_json)
        print(f"Parsed as Python dict: {parsed}")

db.close()
print("\n✓ API should now return grouped ingredients to frontend!")

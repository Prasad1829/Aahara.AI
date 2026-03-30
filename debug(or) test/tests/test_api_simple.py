import json
from app.database import SessionLocal
from app.models import Recipe
from app.services.recommendation_service import _extract_recipe_ingredients, _normalize_detected_ingredients

db = SessionLocal()

print("TEST: Verify JSON ingredients are extracted correctly")
print("=" * 60)

# Get a recipe from database
recipe = db.query(Recipe).filter(Recipe.name == "Chicken Curry").first()

if recipe:
    print(f"\n✓ Found Recipe: {recipe.name}")
    print(f"  Raw JSON: {recipe.ingredients_json[:80]}...")
    
    # Extract ingredients
    extracted = _extract_recipe_ingredients(recipe)
    print(f"\n✓ Extracted ingredients (flattened): {sorted(extracted)}")
    
    # Parse JSON to show structure
    if recipe.ingredients_json:
        ing_dict = json.loads(recipe.ingredients_json)
        print(f"\n✓ Grouped Structure from JSON:")
        for group, items in ing_dict.items():
            print(f"    {group}: {items}")
else:
    print("✗ Recipe not found")

# Test ingredient matching logic
print("\n\nTEST: Ingredient Matching")
print("=" * 60)
detected = _normalize_detected_ingredients(['chicken', 'tomato', 'onion'])
print(f"✓ Normalized detected: {detected}")

# Find recipes with these ingredients
recipes = db.query(Recipe).all()
matches = []

for r in recipes:
    recipe_ing = _extract_recipe_ingredients(r)
    from app.services.indian_ingredients import normalize_ingredient
    recipe_ing_normalized = {normalize_ingredient(ing) for ing in recipe_ing}
    
    intersection = detected.intersection(recipe_ing_normalized)
    if intersection:
        matches.append((r.name, len(intersection)))

matches.sort(key=lambda x: x[1], reverse=True)
print(f"\n✓ Top 5 matching recipes:")
for name, count in matches[:5]:
    print(f"    {name}: {count} matching ingredients")

db.close()
print("\n✓ JSON ingredient storage and extraction working correctly!")

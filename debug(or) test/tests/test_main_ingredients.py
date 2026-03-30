"""
Test the refactored recommendation algorithm
Only main ingredients are used for scoring
"""
import json
from app.database import SessionLocal
from app.models import Recipe
from app.services.recommendation_service import get_recipe_recommendations, _extract_main_ingredients

db = SessionLocal()

print("=" * 70)
print("TEST 1: Algorithm using only MAIN ingredients")
print("=" * 70)
print()

# Test case: Detected ingredients
detected = ["chicken", "tomato", "onion"]
print(f"Detected Ingredients: {detected}")
print()

# Get recommendations
results = get_recipe_recommendations(detected)

print(f"Results Found: {len(results['recommended_recipes'])} recipes")
print()

if results['recommended_recipes']:
    print("TOP RECOMMENDATIONS (sorted by match score):")
    print("-" * 70)
    for i, recipe in enumerate(results['recommended_recipes'][:10], 1):
        print(f"\n{i}. {recipe['name']}")
        print(f"   Match Score: {recipe['match_score']} (out of 1.0)")
        print(f"   Matched Main: {recipe['matched_ingredients']}")
        print(f"   Missing Main: {recipe['missing_ingredients']}")
        print(f"   Vegetarian: {'Yes' if recipe['is_veg'] else 'No'}")
else:
    print("No recipes found")

# Test case 2: Vegetarian preference
print("\n" + "=" * 70)
print("TEST 2: Same ingredients with VEG preference only")
print("=" * 70)
print()

veg_results = get_recipe_recommendations(detected, preference="veg")
print(f"Vegetarian recipes found: {len(veg_results['recommended_recipes'])}")
if veg_results['recommended_recipes']:
    for i, recipe in enumerate(veg_results['recommended_recipes'][:5], 1):
        print(f"  {i}. {recipe['name']} (score: {recipe['match_score']})")

# Test case 3: Verify algorithm logic
print("\n" + "=" * 70)
print("TEST 3: Verify Algorithm Logic for Chicken Curry")
print("=" * 70)
print()

recipe = db.query(Recipe).filter(Recipe.name == "Chicken Curry").first()
if recipe:
    print(f"Recipe: {recipe.name}")
    
    # Show ingredients structure
    if recipe.ingredients_json:
        ing_dict = json.loads(recipe.ingredients_json)
        print(f"\nFull Ingredient Structure:")
        for group, items in ing_dict.items():
            print(f"  {group}: {items}")
    
    # Show main ingredients
    main = _extract_main_ingredients(recipe)
    print(f"\nMAIN ingredients (used for scoring): {sorted(main)}")
    
    # Calculate score manually
    detected_set = set(detected)
    matched = detected_set.intersection(main)
    score = len(matched) / len(main) if main else 0
    
    print(f"\nScore Calculation:")
    print(f"  Detected: {sorted(detected_set)}")
    print(f"  Matched with main: {sorted(matched)}")
    print(f"  Score = {len(matched)} / {len(main)} = {score:.2f}")
    print(f"  ✓ Passes 0.5 threshold: {score >= 0.5}")

db.close()
print("\n✓ Refactored algorithm test complete!")

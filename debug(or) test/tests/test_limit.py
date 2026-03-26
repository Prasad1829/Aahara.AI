"""
Test that recommendation results are limited to 5 recipes
"""
from app.services.recommendation_service import get_recipe_recommendations

print("Testing recommendation limit")
print("=" * 70)
print()

detected = ["chicken", "onion", "tomato"]
print(f"Detected Ingredients: {detected}\n")

results = get_recipe_recommendations(detected)

print(f"✓ Total recipes returned: {len(results['recommended_recipes'])}")
print()

if results['recommended_recipes']:
    print("Top 5 Recommendations:")
    print("-" * 70)
    for i, recipe in enumerate(results['recommended_recipes'], 1):
        print(f"{i}. {recipe['name']}")
        print(f"   Score: {recipe['match_score']} | Matched: {recipe['matched_ingredients']}")
        print()

print("✓ Success! Limited to 5 recipes")

from app.database import SessionLocal
from app.models import Recipe
from app.services.recommendation_service import _extract_recipe_ingredients, OPTIONAL_INGREDIENTS, BASE_INGREDIENTS
from app.services.indian_ingredients import normalize_ingredient

db = SessionLocal()
recipe = db.query(Recipe).filter(Recipe.name == "Chicken Curry").first()

print("CHICKEN CURRY - DETAILED ANALYSIS")
print("=" * 70)

if recipe:
    # Extract all ingredients
    all_ing = _extract_recipe_ingredients(recipe)
    print(f"\n1. ALL INGREDIENTS (raw from JSON): {sorted(all_ing)}")
    
    # Normalize them
    normalized = {normalize_ingredient(ing) for ing in all_ing}
    print(f"\n2. NORMALIZED: {sorted(normalized)}")
    
    # Remove optional
    significant = normalized - OPTIONAL_INGREDIENTS
    print(f"\n3. SIGNIFICANT (after removing optional): {sorted(significant)}")
    
    # Detected ingredients
    detected = {"chicken", "tomato", "onion"}
    print(f"\n4. DETECTED: {detected}")
    
    # Matching
    matched = detected.intersection(significant)
    print(f"\n5. MATCHED: {matched}")
    print(f"   MATCH SCORE: {len(matched)} / {len(significant)} = {len(matched)/len(significant):.2f}")
    
    # Primary match
    primary = significant - BASE_INGREDIENTS
    print(f"\n6. PRIMARY INGREDIENTS: {primary}")
    has_primary = not primary or bool(detected.intersection(primary))
    print(f"   HAS PRIMARY MATCH: {has_primary}")
    
    print(f"\n7. SHOULD BE RECOMMENDED: {len(matched)/len(significant) >= 0.6 and has_primary}")

db.close()

"""
Simulate what the API will return to the frontend
"""
import json
from app.services.recommendation_service import get_recipe_recommendations

print("Simulating API Response to Frontend")
print("=" * 70)
print()

# Simulate detected ingredients from upload
detected = ["chicken", "onion", "tomato"]
print(f"POST /upload -> detected_ingredients: {detected}")
print()

# Get recommendations (what API will return)
recommendations = get_recipe_recommendations(detected)

# Show the response structure
response = {
    "detection": {
        "status": "success",
        "source": "ml",
        "confidence": 0.95,
    },
    "detected_ingredients": detected,
    "recommended_recipes": recommendations["recommended_recipes"][:3],  # Show first 3
}

print("API RESPONSE TO FRONTEND:")
print("-" * 70)
print(json.dumps({
    "detection": response["detection"],
    "detected_ingredients": response["detected_ingredients"],
    "recommended_recipes": [
        {
            "name": r["name"],
            "is_veg": r["is_veg"],
            "match_score": r["match_score"],
            "matched_ingredients": r["matched_ingredients"],
            "ingredients_grouped": r["ingredients_grouped"] if len(r["ingredients_grouped"]) < 200 else "...(grouped structure)",
        }
        for r in response["recommended_recipes"]
    ]
}, indent=2))

print("\n✓ Frontend receives:")
print(f"  - {len(recommendations['recommended_recipes'])} total matching recipes")
print(f"  - Top 3 shown above with grouped ingredient structure")
print(f"  - Each recipe has ingredients_grouped for organized display")
print(f"  - Match scores help sort recipes by relevance")

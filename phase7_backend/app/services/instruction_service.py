import json
from google import genai

GEMINI_API_KEY = "AIzaSyDjmbzLwJHPKfDnhX6UaAS6NqEQ2m0pP-A"
client = genai.Client(api_key=GEMINI_API_KEY)


def generate_recipe_instructions(
    ingredients: list,
    diet: str = "vegetarian",
    spice_level: str = "medium",
    cooking_time: str = "normal"
) -> dict:

    if not ingredients:
        return {"status": "error", "message": "No ingredients provided"}

    time_instruction = "under 20 minutes" if cooking_time == "quick" else "any duration"

    prompt = f"""
You are AHARA AI, an expert Indian recipe assistant.

Given these detected ingredients: {', '.join(ingredients)}

Generate a detailed recipe with these user preferences:
- Diet type: {diet}
- Spice level: {spice_level}
- Cooking time: {time_instruction}

Respond ONLY in this exact JSON format (no extra text):
{{
    "recipe_name": "Recipe name here",
    "prep_time": "X mins",
    "cook_time": "X mins",
    "difficulty": "Easy/Medium/Hard",
    "serves": "X-X people",
    "ingredients_used": ["ingredient1", "ingredient2"],
    "additional_ingredients": ["salt", "oil", "spices needed"],
    "instructions": [
        "Step 1: ...",
        "Step 2: ...",
        "Step 3: ...",
        "Step 4: ...",
        "Step 5: ..."
    ],
    "tips": "One helpful cooking tip here",
    "nutrition_note": "Brief nutrition info here"
}}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        text = response.text.strip()

        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        recipe = json.loads(text)
        recipe["status"] = "success"
        return recipe

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            return {
                "status": "error",
                "message": "Too many requests. Please wait 1 minute and try again.",
                "ingredients": ingredients
            }
        return {
            "status": "error",
            "message": f"Gemini API error: {error_msg}",
            "ingredients": ingredients
             }   


if __name__ == "__main__":
    print("=" * 50)
    print("  AHARA AI — Instruction Generation Test")
    print("=" * 50)

    test_ingredients = ["carrot", "onion", "tomato", "garlic", "ginger"]

    print(f"\n🥦 Ingredients: {test_ingredients}")
    print("🍽️  Preferences: vegetarian, medium spice, quick cooking")
    print("\n⏳ Generating recipe with Gemini AI...\n")

    result = generate_recipe_instructions(
        ingredients=test_ingredients,
        diet="vegetarian",
        spice_level="medium",
        cooking_time="quick"
    )

    if result["status"] == "success":
        print(f"✅ Recipe: {result['recipe_name']}")
        print(f"⏱️  Prep: {result['prep_time']} | Cook: {result['cook_time']}")
        print(f"👨‍🍳 Difficulty: {result['difficulty']} | Serves: {result['serves']}")
        print(f"\n📋 Instructions:")
        for step in result["instructions"]:
            print(f"   {step}")
        print(f"\n💡 Tip: {result['tips']}")
    else:
        print(f"❌ Error: {result['message']}")

    print("=" * 50)
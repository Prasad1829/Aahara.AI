import json
import time
from app.services.ai_service import generate_text, FRIENDLY_ERROR_MESSAGE

_INSTRUCTION_CACHE: dict[str, dict] = {}
_CACHE_TTL_SECONDS = 15 * 60


def _cache_get(cache_key: str) -> dict | None:
    item = _INSTRUCTION_CACHE.get(cache_key)
    if not item:
        return None
    if time.time() - item["ts"] > _CACHE_TTL_SECONDS:
        _INSTRUCTION_CACHE.pop(cache_key, None)
        return None
    return item["value"]


def _cache_set(cache_key: str, value: dict) -> None:
    _INSTRUCTION_CACHE[cache_key] = {"ts": time.time(), "value": value}


def _build_cache_key(ingredients: list, diet: str, spice_level: str, cooking_time: str) -> str:
    normalized = [i.strip().lower() for i in ingredients if i]
    normalized.sort()
    return f"{'|'.join(normalized)}::{diet}::{spice_level}::{cooking_time}"


def generate_recipe_instructions(
    ingredients: list,
    diet: str = "vegetarian",
    spice_level: str = "medium",
    cooking_time: str = "normal"
) -> dict:

    if not ingredients:
        return {"status": "error", "message": "No ingredients provided"}

    cache_key = _build_cache_key(ingredients, diet, spice_level, cooking_time)
    cached = _cache_get(cache_key)
    if cached:
        cached_copy = dict(cached)
        cached_copy["cached"] = True
        return cached_copy

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
        text = generate_text(prompt)

        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        recipe = json.loads(text)
        recipe["status"] = "success"
        _cache_set(cache_key, recipe)
        return recipe

    except Exception:
        return {
            "status": "error",
            "code": "ai_unavailable",
            "message": FRIENDLY_ERROR_MESSAGE,
            "ingredients": ingredients,
        }


def generate_gemini_chat_reply(
    messages: list[dict],
    ingredients: list[str] | None = None,
    diet: str = "vegetarian",
    spice_level: str = "medium",
    cooking_time: str = "normal",
    recipe_name: str | None = None,
) -> dict:

    if not messages:
        return {"status": "error", "message": "No messages provided"}

    time_instruction = "under 20 minutes" if cooking_time == "quick" else "any duration"
    ingredients_text = ", ".join(ingredients) if ingredients else "not provided"
    recipe_text = recipe_name or "this recipe"

    conversation_lines = []
    for msg in messages:
        role = (msg.get("role") or "user").lower()
        content = msg.get("content") or msg.get("text") or ""
        if not content:
            continue
        prefix = "User" if role == "user" else "Assistant"
        conversation_lines.append(f"{prefix}: {content}")

    prompt = f"""
You are AHARA AI, an expert Indian recipe assistant.

Context:
- Recipe: {recipe_text}
- Ingredients: {ingredients_text}
- Diet: {diet}
- Spice level: {spice_level}
- Cooking time: {time_instruction}

Conversation so far:
{chr(10).join(conversation_lines)}

Provide a helpful, concise response. If the user asks for substitutions or steps, answer clearly.
Respond in plain text only.
"""

    try:
        text = generate_text(prompt)
        return {"status": "success", "reply": text}
    except Exception:
        return {
            "status": "error",
            "code": "ai_unavailable",
            "message": FRIENDLY_ERROR_MESSAGE,
        }


def _fallback_chat_reply(ingredients, recipe_name, diet, spice_level, cooking_time):
    return FRIENDLY_ERROR_MESSAGE


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

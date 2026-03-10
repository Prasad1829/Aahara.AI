from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.services.instruction_service import generate_recipe_instructions, generate_gemini_chat_reply
from app.database import get_db
from app.models import Recipe
from sqlalchemy.orm import Session

router = APIRouter()


class UserPreferences(BaseModel):
    diet: str = "vegetarian"
    spice_level: str = "medium"
    cooking_time: str = "normal"


class InstructionRequest(BaseModel):
    ingredients: List[str]
    recipe_name: Optional[str] = None
    preferences: Optional[UserPreferences] = None


class ChatMessage(BaseModel):
    role: str
    content: str


class GeminiChatRequest(BaseModel):
    messages: List[ChatMessage]
    ingredients: Optional[List[str]] = None
    recipe_name: Optional[str] = None
    preferences: Optional[UserPreferences] = None


def _fallback_instructions(ingredients: list[str], prefs: UserPreferences) -> list[str]:
    base = [
        "Step 1: Prep and wash all ingredients. Chop aromatics and main items.",
        "Step 2: Heat oil in a pan. Sauté onions until golden.",
        "Step 3: Add ginger-garlic and sauté briefly. Add spices and stir for 30–60 seconds.",
        "Step 4: Add main ingredients and mix well. Cook on medium heat.",
        "Step 5: Add water as needed. Simmer until cooked to your preferred consistency.",
        "Step 6: Adjust salt and spice. Finish with herbs and serve hot.",
    ]
    return base


@router.post("/generate-instructions")
async def generate_instructions(request: InstructionRequest, db: Session = Depends(get_db)):
    if not request.ingredients:
        raise HTTPException(
            status_code=400,
            detail="No ingredients provided"
        )

    prefs = request.preferences or UserPreferences()

    result = generate_recipe_instructions(
        ingredients=request.ingredients,
        diet=prefs.diet,
        spice_level=prefs.spice_level,
        cooking_time=prefs.cooking_time
    )

    if result["status"] == "error":
        if request.recipe_name:
            recipe = db.query(Recipe).filter(Recipe.name == request.recipe_name).first()
            if recipe and recipe.instructions:
                instructions = [s.strip() for s in recipe.instructions.split("\n") if s.strip()]
                return {"status": "success", "instructions": instructions, "source": "db_fallback"}
        # Generic fallback to avoid hard failure when Gemini is rate limited.
        return {"status": "success", "instructions": _fallback_instructions(request.ingredients, prefs), "source": "generic_fallback"}

    return result


@router.post("/gemini-chat")
async def gemini_chat(request: GeminiChatRequest):
    prefs = request.preferences or UserPreferences()
    result = generate_gemini_chat_reply(
        messages=[m.dict() for m in request.messages],
        ingredients=request.ingredients or [],
        diet=prefs.diet,
        spice_level=prefs.spice_level,
        cooking_time=prefs.cooking_time,
        recipe_name=request.recipe_name,
    )

    if result["status"] == "error":
        return {
            "status": "success",
            "reply": "Assistant temporarily unavailable. Please try again.",
            "fallback": True,
        }

    return result

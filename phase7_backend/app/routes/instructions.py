from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.instruction_service import generate_recipe_instructions

router = APIRouter()


class UserPreferences(BaseModel):
    diet: str = "vegetarian"
    spice_level: str = "medium"
    cooking_time: str = "normal"


class InstructionRequest(BaseModel):
    ingredients: List[str]
    preferences: Optional[UserPreferences] = None


@router.post("/generate-instructions")
async def generate_instructions(request: InstructionRequest):
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
        raise HTTPException(
            status_code=500,
            detail=result.get("message", "Failed to generate instructions")
        )

    return result

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Recipe, User, RecipeHistory
from app.schemas.history import HistoryCreate, HistoryItem
from app.services.image_service import get_cached_recipe_image_url, get_recipe_image_url

router = APIRouter(prefix="/history", tags=["history"])


def _serialize(recipe: Recipe | None, history: RecipeHistory, db: Session) -> dict:
    name = recipe.name if recipe else history.recipe_name
    return {
        "id": history.id,
        "recipe_name": name,
        "is_veg": recipe.is_veg if recipe else None,
        "cooking_time_minutes": recipe.cooking_time_minutes if recipe else None,
        "image_url": get_cached_recipe_image_url(recipe, db) if recipe else get_recipe_image_url(name),
    }


@router.get("", response_model=list[HistoryItem])
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = (
        db.query(RecipeHistory)
        .filter(RecipeHistory.user_id == current_user.id)
        .order_by(RecipeHistory.viewed_at.desc())
        .limit(20)
        .all()
    )
    results = []
    for item in items:
        recipe = db.query(Recipe).filter(Recipe.id == item.recipe_id).first() if item.recipe_id else None
        results.append(_serialize(recipe, item, db))
    return results


@router.post("", response_model=HistoryItem)
def add_history(
    payload: HistoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not payload.recipe_id and not payload.recipe_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="recipe_id or recipe_name is required",
        )

    recipe = None
    name = None
    if payload.recipe_id:
        recipe = db.query(Recipe).filter(Recipe.id == payload.recipe_id).first()
        if recipe:
            name = recipe.name
    if name is None and payload.recipe_name:
        name = payload.recipe_name
        recipe = db.query(Recipe).filter(Recipe.name == payload.recipe_name).first()

    if not name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    item = RecipeHistory(
        user_id=current_user.id,
        recipe_id=recipe.id if recipe else None,
        recipe_name=name,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return _serialize(recipe, item, db)


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history_item(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(RecipeHistory)
        .filter(RecipeHistory.id == history_id, RecipeHistory.user_id == current_user.id)
        .first()
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History item not found")
    db.delete(item)
    db.commit()
    return None

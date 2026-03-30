from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Recipe, User, Wishlist
from app.schemas.wishlist import WishlistCreate, WishlistRecipe
from app.services.image_service import FALLBACK_IMAGE_URL, get_cached_recipe_image_url

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


def _serialize_recipe(recipe: Recipe, db: Session) -> dict:
    return {
        "id": recipe.id,
        "name": recipe.name,
        "is_veg": recipe.is_veg,
        "cooking_time_minutes": recipe.cooking_time_minutes,
        "image_url": get_cached_recipe_image_url(recipe, db),
        "image_fallback_url": FALLBACK_IMAGE_URL,
    }


@router.get("", response_model=list[WishlistRecipe])
def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = (
        db.query(Recipe)
        .join(Wishlist, Wishlist.recipe_id == Recipe.id)
        .filter(Wishlist.user_id == current_user.id)
        .order_by(Wishlist.created_at.desc())
        .all()
    )
    return [_serialize_recipe(item, db) for item in items]


@router.post("", response_model=WishlistRecipe)
def add_to_wishlist(
    payload: WishlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not payload.recipe_id and not payload.recipe_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="recipe_id or recipe_name is required",
        )

    if payload.recipe_id:
        recipe = db.query(Recipe).filter(Recipe.id == payload.recipe_id).first()
    else:
        recipe = db.query(Recipe).filter(Recipe.name == payload.recipe_name).first()

    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    existing = (
        db.query(Wishlist)
        .filter(Wishlist.user_id == current_user.id, Wishlist.recipe_id == recipe.id)
        .first()
    )
    if existing:
        return _serialize_recipe(recipe, db)

    wishlist = Wishlist(user_id=current_user.id, recipe_id=recipe.id)
    db.add(wishlist)
    db.commit()
    return _serialize_recipe(recipe, db)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_wishlist(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(Wishlist)
        .filter(Wishlist.user_id == current_user.id, Wishlist.recipe_id == recipe_id)
        .first()
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wishlist item not found")
    db.delete(item)
    db.commit()
    return None

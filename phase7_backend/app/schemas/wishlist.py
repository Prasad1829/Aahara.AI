from pydantic import BaseModel


class WishlistCreate(BaseModel):
    recipe_id: int | None = None
    recipe_name: str | None = None


class WishlistRecipe(BaseModel):
    id: int
    name: str
    is_veg: bool | None = None
    cooking_time_minutes: int | None = None
    image_url: str | None = None
    image_fallback_url: str | None = None

    class Config:
        orm_mode = True

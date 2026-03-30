from pydantic import BaseModel


class HistoryCreate(BaseModel):
    recipe_id: int | None = None
    recipe_name: str | None = None


class HistoryItem(BaseModel):
    id: int
    recipe_name: str
    is_veg: bool | None = None
    cooking_time_minutes: int | None = None
    image_url: str | None = None

    class Config:
        orm_mode = True

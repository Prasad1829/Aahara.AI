from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

recipe_ingredients = Table(
    "recipe_ingredients",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id"), primary_key=True),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    wishlists = relationship("Wishlist", back_populates="user", cascade="all, delete-orphan")
    history_items = relationship("RecipeHistory", back_populates="user", cascade="all, delete-orphan")


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    is_veg = Column(Boolean, default=True, nullable=False)
    cooking_time_minutes = Column(Integer, default=30, nullable=False)
    instructions = Column(Text, default="", nullable=False)
    image_url = Column(String, nullable=True)

    ingredients = relationship(
        "Ingredient",
        secondary=recipe_ingredients,
        back_populates="recipes",
    )

    wishlisted_by = relationship("Wishlist", back_populates="recipe", cascade="all, delete-orphan")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    recipes = relationship(
        "Recipe",
        secondary=recipe_ingredients,
        back_populates="ingredients",
    )


class Wishlist(Base):
    __tablename__ = "wishlists"
    __table_args__ = (
        UniqueConstraint("user_id", "recipe_id", name="uq_wishlist_user_recipe"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="wishlists")
    recipe = relationship("Recipe", back_populates="wishlisted_by")


class RecipeHistory(Base):
    __tablename__ = "recipe_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=True, index=True)
    recipe_name = Column(String, nullable=False)
    viewed_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="history_items")
    recipe = relationship("Recipe")


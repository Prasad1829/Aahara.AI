from datetime import datetime
from app.mongodb import Field


class User:
    __collection_name__ = "users"

    id = Field("id")
    email = Field("email")
    hashed_password = Field("hashed_password")
    full_name = Field("full_name")
    phone_number = Field("phone_number")
    avatar_url = Field("avatar_url")
    auth_provider = Field("auth_provider")
    provider_subject = Field("provider_subject")

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.email = kwargs.get("email")
        self.hashed_password = kwargs.get("hashed_password")
        self.full_name = kwargs.get("full_name")
        self.phone_number = kwargs.get("phone_number")
        self.avatar_url = kwargs.get("avatar_url")
        self.auth_provider = kwargs.get("auth_provider")
        self.provider_subject = kwargs.get("provider_subject")
        self._session = None

    @classmethod
    def from_doc(cls, doc, session=None):
        cleaned = {k: v for k, v in doc.items() if k != "_id"}
        obj = cls(**cleaned)
        obj._session = session
        return obj

    def save(self, db):
        if not self.id:
            max_user = db["users"].find_one(sort=[("id", -1)])
            self.id = (max_user["id"] + 1) if (max_user and "id" in max_user) else 1

        doc = {
            "id": self.id,
            "email": self.email,
            "hashed_password": self.hashed_password,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "avatar_url": self.avatar_url,
            "auth_provider": self.auth_provider,
            "provider_subject": self.provider_subject,
        }
        db["users"].update_one({"id": self.id}, {"$set": doc}, upsert=True)

    def delete_from_db(self, db):
        if self.id:
            db["users"].delete_one({"id": self.id})

    def reload(self, db):
        doc = db["users"].find_one({"email": self.email}) if self.email else db["users"].find_one({"id": self.id})
        if doc:
            for k, v in doc.items():
                if k != "_id" and hasattr(self, k):
                    setattr(self, k, v)


class Ingredient:
    __collection_name__ = "ingredients"

    id = Field("id")
    name = Field("name")

    def __init__(self, name="", id=None):
        self.id = id
        self.name = name

    @classmethod
    def from_doc(cls, doc, session=None):
        return cls(name=doc.get("name", ""), id=doc.get("id"))

    def save(self, db):
        pass

    def delete_from_db(self, db):
        pass


class Recipe:
    __collection_name__ = "recipes"

    id = Field("id")
    name = Field("name")
    is_veg = Field("is_veg")

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name", "")
        self.is_veg = kwargs.get("is_veg", True)
        self.cooking_time_minutes = kwargs.get("cooking_time_minutes", 30)
        self.instructions = kwargs.get("instructions", "")
        self.image_url = kwargs.get("image_url", "")
        self._session = None

        raw_ings = kwargs.get("ingredients", [])
        self._ingredients = []
        for ing in raw_ings:
            if isinstance(ing, str):
                self._ingredients.append(Ingredient(name=ing))
            elif isinstance(ing, Ingredient):
                self._ingredients.append(ing)
            elif isinstance(ing, dict):
                self._ingredients.append(Ingredient(name=ing.get("name", "")))

    @property
    def ingredients(self):
        return self._ingredients

    @ingredients.setter
    def ingredients(self, val):
        self._ingredients = val

    @classmethod
    def from_doc(cls, doc, session=None):
        cleaned = {k: v for k, v in doc.items() if k != "_id"}
        obj = cls(**cleaned)
        obj._session = session
        return obj

    def save(self, db):
        if not self.id:
            max_rec = db["recipes"].find_one(sort=[("id", -1)])
            self.id = (max_rec["id"] + 1) if (max_rec and "id" in max_rec) else 1

        ing_names = []
        for ing in self._ingredients:
            if isinstance(ing, str):
                ing_names.append(ing)
            elif hasattr(ing, "name"):
                ing_names.append(ing.name)

        doc = {
            "id": self.id,
            "name": self.name,
            "is_veg": self.is_veg,
            "cooking_time_minutes": self.cooking_time_minutes,
            "instructions": self.instructions,
            "image_url": self.image_url,
            "ingredients": ing_names,
        }
        db["recipes"].update_one({"id": self.id}, {"$set": doc}, upsert=True)

    def delete_from_db(self, db):
        if self.id:
            db["recipes"].delete_one({"id": self.id})

    def reload(self, db):
        doc = db["recipes"].find_one({"id": self.id})
        if doc:
            for k, v in doc.items():
                if k != "_id" and hasattr(self, k):
                    setattr(self, k, v)


class Wishlist:
    __collection_name__ = "wishlists"

    id = Field("id")
    user_id = Field("user_id")
    recipe_id = Field("recipe_id")
    created_at = Field("created_at")

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.user_id = kwargs.get("user_id")
        self.recipe_id = kwargs.get("recipe_id")
        self.created_at = kwargs.get("created_at") or datetime.utcnow()
        self._session = None

    @classmethod
    def from_doc(cls, doc, session=None):
        cleaned = {k: v for k, v in doc.items() if k != "_id"}
        obj = cls(**cleaned)
        obj._session = session
        return obj

    @property
    def recipe(self):
        if self.recipe_id and self._session:
            return self._session.query(Recipe).filter(Recipe.id == self.recipe_id).first()
        return None

    def save(self, db):
        if not self.id:
            max_w = db["wishlists"].find_one(sort=[("id", -1)])
            self.id = (max_w["id"] + 1) if (max_w and "id" in max_w) else 1

        doc = {
            "id": self.id,
            "user_id": self.user_id,
            "recipe_id": self.recipe_id,
            "created_at": self.created_at,
        }
        db["wishlists"].update_one({"id": self.id}, {"$set": doc}, upsert=True)

    def delete_from_db(self, db):
        if self.id:
            db["wishlists"].delete_one({"id": self.id})


class RecipeHistory:
    __collection_name__ = "recipe_history"

    id = Field("id")
    user_id = Field("user_id")
    recipe_id = Field("recipe_id")
    viewed_at = Field("viewed_at")

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.user_id = kwargs.get("user_id")
        self.recipe_id = kwargs.get("recipe_id")
        self.recipe_name = kwargs.get("recipe_name", "")
        self.viewed_at = kwargs.get("viewed_at") or datetime.utcnow()
        self._session = None

    @classmethod
    def from_doc(cls, doc, session=None):
        cleaned = {k: v for k, v in doc.items() if k != "_id"}
        obj = cls(**cleaned)
        obj._session = session
        return obj

    @property
    def recipe(self):
        if self.recipe_id and self._session:
            return self._session.query(Recipe).filter(Recipe.id == self.recipe_id).first()
        return None

    def save(self, db):
        if not self.id:
            max_h = db["recipe_history"].find_one(sort=[("id", -1)])
            self.id = (max_h["id"] + 1) if (max_h and "id" in max_h) else 1

        doc = {
            "id": self.id,
            "user_id": self.user_id,
            "recipe_id": self.recipe_id,
            "recipe_name": self.recipe_name,
            "viewed_at": self.viewed_at,
        }
        db["recipe_history"].update_one({"id": self.id}, {"$set": doc}, upsert=True)

    def delete_from_db(self, db):
        if self.id:
            db["recipe_history"].delete_one({"id": self.id})

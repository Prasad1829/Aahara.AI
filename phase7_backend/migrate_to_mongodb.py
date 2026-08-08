import sqlite3
import pymongo
import json
import os
from datetime import datetime

MONGODB_URL = os.getenv(
    "MONGODB_URL",
    "mongodb+srv://prasad10052004_db_user:cQB5GIq5x4ASOm3J@cluster0.ejqcczp.mongodb.net/aahara_ai?appName=Cluster0"
)

def migrate():
    print("🚀 Connecting to MongoDB Atlas...")
    client = pymongo.MongoClient(MONGODB_URL)
    mongo_db = client.get_database()

    sqlite_path = os.path.join(os.path.dirname(__file__), "recipe.db")
    if not os.path.exists(sqlite_path):
        print(f"⚠️ SQLite database file not found at {sqlite_path}. Skipping data transfer.")
        return

    print("📖 Reading data from SQLite recipe.db...")
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Migrate Recipes & Ingredients
    cursor.execute("""
        SELECT r.id, r.name, r.is_veg, r.cooking_time_minutes, r.instructions, r.image_url,
               GROUP_CONCAT(i.name) as ingredients
        FROM recipes r
        LEFT JOIN recipe_ingredients ri ON r.id = ri.recipe_id
        LEFT JOIN ingredients i ON ri.ingredient_id = i.id
        GROUP BY r.id;
    """)
    recipes_rows = cursor.fetchall()
    print(f"📦 Found {len(recipes_rows)} recipes in SQLite.")

    recipes_col = mongo_db["recipes"]
    recipes_col.create_index("name", unique=True)
    recipes_col.create_index("id", unique=True)

    recipes_migrated = 0
    for row in recipes_rows:
        ing_list = []
        if row["ingredients"]:
            ing_list = [ing.strip().lower() for ing in row["ingredients"].split(",") if ing.strip()]

        recipe_doc = {
            "id": int(row["id"]),
            "name": row["name"],
            "is_veg": bool(row["is_veg"]),
            "cooking_time_minutes": int(row["cooking_time_minutes"]) if row["cooking_time_minutes"] else 30,
            "instructions": row["instructions"] or "",
            "image_url": row["image_url"] or "",
            "ingredients": ing_list
        }

        recipes_col.update_one(
            {"id": recipe_doc["id"]},
            {"$set": recipe_doc},
            upsert=True
        )
        recipes_migrated += 1

    print(f"✅ Migrated {recipes_migrated} recipes into MongoDB Atlas collection 'recipes'.")

    # 2. Migrate Users
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    if cursor.fetchone():
        cursor.execute("SELECT * FROM users;")
        users_rows = cursor.fetchall()
        users_col = mongo_db["users"]
        users_col.create_index("email", unique=True)
        users_col.create_index("id", unique=True)

        users_migrated = 0
        for row in users_rows:
            user_dict = dict(row)
            user_dict["id"] = int(user_dict["id"])
            users_col.update_one(
                {"id": user_dict["id"]},
                {"$set": user_dict},
                upsert=True
            )
            users_migrated += 1
        print(f"✅ Migrated {users_migrated} users into MongoDB Atlas collection 'users'.")

    # 3. Migrate Wishlists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wishlists';")
    if cursor.fetchone():
        cursor.execute("SELECT * FROM wishlists;")
        wish_rows = cursor.fetchall()
        wish_col = mongo_db["wishlists"]
        wish_col.create_index([("user_id", 1), ("recipe_id", 1)], unique=True)

        wish_migrated = 0
        for row in wish_rows:
            w_dict = dict(row)
            w_dict["id"] = int(w_dict["id"])
            w_dict["user_id"] = int(w_dict["user_id"])
            w_dict["recipe_id"] = int(w_dict["recipe_id"])
            wish_col.update_one(
                {"id": w_dict["id"]},
                {"$set": w_dict},
                upsert=True
            )
            wish_migrated += 1
        print(f"✅ Migrated {wish_migrated} wishlist entries into MongoDB Atlas collection 'wishlists'.")

    # 4. Migrate History
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='recipe_history';")
    if cursor.fetchone():
        cursor.execute("SELECT * FROM recipe_history;")
        hist_rows = cursor.fetchall()
        hist_col = mongo_db["recipe_history"]

        hist_migrated = 0
        for row in hist_rows:
            h_dict = dict(row)
            h_dict["id"] = int(h_dict["id"])
            h_dict["user_id"] = int(h_dict["user_id"])
            if h_dict.get("recipe_id"):
                h_dict["recipe_id"] = int(h_dict["recipe_id"])
            hist_col.update_one(
                {"id": h_dict["id"]},
                {"$set": h_dict},
                upsert=True
            )
            hist_migrated += 1
        print(f"✅ Migrated {hist_migrated} history entries into MongoDB Atlas collection 'recipe_history'.")

    conn.close()
    print("🎉 All data successfully migrated to MongoDB Atlas!")

if __name__ == "__main__":
    migrate()

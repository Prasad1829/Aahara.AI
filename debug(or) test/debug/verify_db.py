import sqlite3
import json

conn = sqlite3.connect('recipe.db')
cursor = conn.cursor()

# Check recipes
cursor.execute("SELECT COUNT(*) FROM recipes;")
count = cursor.fetchone()[0]
print(f"✓ Total recipes in DB: {count}\n")

# Show structure of a sample recipe
cursor.execute("SELECT name, is_veg, ingredients_json FROM recipes LIMIT 1;")
recipe = cursor.fetchone()

if recipe:
    name, is_veg, ing_json = recipe
    print(f"Sample Recipe: {name}")
    print(f"  Is Vegetarian: {bool(is_veg)}")
    print(f"  Ingredients (Grouped):")
    
    if ing_json:
        try:
            ing_dict = json.loads(ing_json)
            for group, items in ing_dict.items():
                print(f"    {group}: {items}")
        except json.JSONDecodeError:
            print(f"    ERROR: Could not parse JSON")
    else:
        print(f"    (No ingredients stored)")

# Show another example - Chicken Curry
print("\n---")
cursor.execute("SELECT name, is_veg, ingredients_json FROM recipes WHERE name='Chicken Curry';")
recipe = cursor.fetchone()

if recipe:
    name, is_veg, ing_json = recipe
    print(f"Sample Recipe: {name}")
    print(f"  Is Vegetarian: {bool(is_veg)}")
    print(f"  Raw JSON: {ing_json}")

conn.close()

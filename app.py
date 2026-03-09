from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import json
import os
from difflib import get_close_matches
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = "change_this_secret_key"

# ---------- DB ----------
def db_conn():
    return sqlite3.connect(os.path.join(BASE_DIR, "database.db"))

def init_db():
    conn = db_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            query TEXT NOT NULL,
            top_result TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS saved(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            recipe_name TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- Recipes ----------
RECIPES_PATH = os.path.join(BASE_DIR, "recipes.json")
with open(RECIPES_PATH, "r", encoding="utf-8") as f:
    RECIPES = json.load(f)

KNOWN_INGREDIENTS = sorted({ing for r in RECIPES for ing in r["ingredients"]})

ALIASES = {
    "panner": "paneer",
    "paner": "paneer",
    "allo": "aloo",
    "baingan": "brinjal",
    "bhindi": "okra",
    "ladyfinger": "okra",
    "ladiesfinger": "okra",
}

def normalize_token(t: str) -> str:
    t = t.strip().lower()
    t = t.replace("-", " ").replace("_", " ").replace(".", "")
    return t

def parse_ingredients(text: str):
    raw = [x for x in text.replace(",", " ").split() if x.strip()]
    tokens = [normalize_token(x) for x in raw]
    fixed = []
    for t in tokens:
        t = ALIASES.get(t, t)
        m = get_close_matches(t, KNOWN_INGREDIENTS, n=1, cutoff=0.72)
        fixed.append(m[0] if m else t)

    out = []
    for x in fixed:
        if x not in out:
            out.append(x)
    return out

def pick_image(recipe_image, user_ings):
    img_dir = os.path.join(BASE_DIR, "static", "images")
    if recipe_image and os.path.exists(os.path.join(img_dir, recipe_image)):
        return recipe_image
    if user_ings:
        cand = f"{user_ings[0]}.jpg"
        if os.path.exists(os.path.join(img_dir, cand)):
            return cand
    return "food.jpg"

def score_recipe(user_ings, recipe_ings):
    user_set = set(user_ings)
    recipe_set = set(recipe_ings)
    matched = sorted(list(user_set & recipe_set))
    missing = sorted(list(recipe_set - user_set))
    score = len(matched) / max(1, len(recipe_set))
    return score, matched, missing

def best_recipes(user_ings, top_k=3):
    scored = []
    for r in RECIPES:
        s, matched, missing = score_recipe(user_ings, r["ingredients"])
        if s > 0:
            scored.append({
                "name": r["name"],
                "image": pick_image(r.get("image"), user_ings),
                "ingredients": r["ingredients"],
                "steps": r["steps"],
                "time": r.get("time", ""),
                "difficulty": r.get("difficulty", ""),
                "cuisine": r.get("cuisine", ""),
                "score": round(s * 100, 1),
                "matched": matched,
                "missing": missing
            })
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]

def fallback_generated_recipe(user_ings):
    main = user_ings[0] if user_ings else "vegetable"
    title = f"{main.capitalize()} Masala"
    base = ["oil", "onion", "tomato", "garlic", "spices", "salt"]

    full_ings = []
    for x in user_ings + base:
        if x not in full_ings:
            full_ings.append(x)

    steps = [
        "Heat oil in a pan. Add chopped onions and sauté until light golden.",
        "Add garlic/ginger (optional) and cook for 30 seconds.",
        "Add chopped tomatoes (or puree) and cook until soft and oil separates.",
        "Add spices (turmeric, chili, garam masala) and salt; mix well.",
        f"Add {main} and a splash of water. Cover and cook until tender.",
        "Finish with coriander and serve hot with roti or rice."
    ]

    return {
        "name": title,
        "image": pick_image(None, user_ings),
        "ingredients": full_ings,
        "steps": steps,
        "time": "25–35 min",
        "difficulty": "Easy",
        "cuisine": "Indian",
        "score": 0.0,
        "matched": user_ings,
        "missing": []
    }

def logged_in():
    return "user" in session

# ---------- Routes ----------
@app.route("/")
def home():
    return render_template("home.html", user=session.get("user"), title="Home")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        if not username or not password:
            return render_template("register.html", error="Username and password required.", user=None, title="Register")

        conn = db_conn()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users(username, password_hash) VALUES(?,?)",
                      (username, generate_password_hash(password)))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("register.html", error="Username already exists.", user=None, title="Register")
        conn.close()
        return redirect(url_for("login"))

    return render_template("register.html", error=None, user=None, title="Register")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = db_conn()
        row = conn.execute("SELECT password_hash FROM users WHERE username=?", (username,)).fetchone()
        conn.close()

        if row and check_password_hash(row[0], password):
            session["user"] = username
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid username or password.", user=None, title="Login")

    return render_template("login.html", error=None, user=None, title="Login")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if not logged_in():
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session.get("user"), title="Dashboard")

@app.route("/api/generate", methods=["POST"])
def api_generate():
    if not logged_in():
        return jsonify({"ok": False, "error": "Not logged in"}), 401

    data = request.get_json(force=True)
    query = (data.get("query") or "").strip()
    if not query:
        return jsonify({"ok": False, "error": "Please enter ingredients"}), 400

    user_ings = parse_ingredients(query)
    top = best_recipes(user_ings, top_k=3)

    if top:
        top_result_name = top[0]["name"]
        payload = {"mode": "matched", "user_ingredients": user_ings, "results": top}
    else:
        gen = fallback_generated_recipe(user_ings)
        top_result_name = gen["name"]
        payload = {"mode": "generated", "user_ingredients": user_ings, "results": [gen]}

    conn = db_conn()
    conn.execute("INSERT INTO history(username, query, top_result) VALUES(?,?,?)",
                 (session["user"], query, top_result_name))
    conn.commit()
    conn.close()

    return jsonify({"ok": True, **payload})

@app.route("/save", methods=["POST"])
def save():
    if not logged_in():
        return redirect(url_for("login"))
    recipe_name = request.form.get("recipe_name", "").strip()
    if recipe_name:
        conn = db_conn()
        conn.execute("INSERT INTO saved(username, recipe_name) VALUES(?,?)", (session["user"], recipe_name))
        conn.commit()
        conn.close()
    return redirect(url_for("saved"))

@app.route("/history")
def history():
    if not logged_in():
        return redirect(url_for("login"))
    conn = db_conn()
    rows = conn.execute(
        "SELECT query, top_result, created_at FROM history WHERE username=? ORDER BY id DESC LIMIT 50",
        (session["user"],)
    ).fetchall()
    conn.close()
    return render_template("history.html", user=session.get("user"), rows=rows, title="History")

@app.route("/saved")
def saved():
    if not logged_in():
        return redirect(url_for("login"))
    conn = db_conn()
    rows = conn.execute(
        "SELECT recipe_name, created_at FROM saved WHERE username=? ORDER BY id DESC",
        (session["user"],)
    ).fetchall()
    conn.close()
    return render_template("saved.html", user=session.get("user"), rows=rows, title="Saved")

if __name__ == "__main__":
    app.run(debug=True)
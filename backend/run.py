import os
import sys
from functools import wraps

from flask import redirect, render_template, request, session, url_for


sys.path.insert(0, os.path.dirname(__file__))

from app import create_app


app = create_app()

app.template_folder = os.path.join(os.path.dirname(__file__), "../frontend/templates")
app.static_folder = os.path.join(os.path.dirname(__file__), "../frontend/static")
app.static_url_path = "/static"

print(f"Template folder: {app.template_folder}")
print(f"Static folder: {app.static_folder}")


def _is_authenticated():
    return bool(session.get("user_id"))


def _is_admin():
    return session.get("user_role") in {"admin", "super_admin"}


def login_required_page(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not _is_authenticated():
            return redirect(url_for("login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapper


def admin_required_page(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not _is_authenticated():
            return redirect(url_for("login", next=request.path))
        if not _is_admin():
            return redirect(url_for("dashboard"))
        return view_func(*args, **kwargs)
    return wrapper


@app.context_processor
def inject_auth_context():
    return {
        "is_authenticated": _is_authenticated(),
        "is_admin": _is_admin(),
        "current_user_role": session.get("user_role", "user"),
        "current_user_id": session.get("user_id"),
        "current_user_name": session.get("user_name"),
        "csrf_token": session.get("csrf_token", ""),
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    if _is_authenticated():
        return redirect(url_for("admin_dashboard" if _is_admin() else "dashboard"))
    return render_template("auth/login.html")


@app.route("/register")
def register():
    if _is_authenticated():
        return redirect(url_for("admin_dashboard" if _is_admin() else "dashboard"))
    return render_template("auth/register.html")


@app.route("/dashboard")
@login_required_page
def dashboard():
    return render_template("dashboard/dashboard.html")


@app.route("/profile")
@login_required_page
def profile():
    return render_template("profile/profile.html")


@app.route("/edit-profile")
@login_required_page
def edit_profile():
    return render_template("profile/edit_profile.html")


@app.route("/upload")
@login_required_page
def upload():
    return render_template("recipe/upload.html")


@app.route("/recipe-results")
@login_required_page
def recipe_results():
    return render_template("recipe/results.html")


@app.route("/recipe-details")
@login_required_page
def recipe_details():
    return render_template("recipe/details.html")


@app.route("/recipe/<int:recipe_id>")
@login_required_page
def recipe_details_by_id(recipe_id):
    return render_template("recipe/details.html", recipe_id=recipe_id)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/my-recipes")
@login_required_page
def my_recipes():
    return render_template("recipe/my_recipes.html")


@app.route("/saved")
@login_required_page
def saved():
    return render_template("recipe/saved.html")


@app.route("/admin")
@admin_required_page
def admin_dashboard():
    return render_template("admin/dashboard.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("Starting Ingredient Recipe AI Backend...")
    print("=" * 50)
    print("Frontend URL: http://localhost:5000")
    print("API URL: http://localhost:5000/api")
    print("=" * 50 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=True)

# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.models import User
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from .models import Recipe, Favorite, SearchHistory


# # =========================
# # REGISTER VIEW
# # =========================
# def register_view(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         email = request.POST.get("email")
#         password = request.POST.get("password")

#         if User.objects.filter(username=username).exists():
#             messages.error(request, "Username already exists")
#             return redirect("register")

#         User.objects.create_user(
#             username=username,
#             email=email,
#             password=password
#         )

#         messages.success(request, "Account created successfully")
#         return redirect("login")

#     return render(request, "register.html")


# # =========================
# # LOGIN VIEW
# # =========================
# def login_view(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")

#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             login(request, user)
#             return redirect("dashboard")
#         else:
#             messages.error(request, "Invalid username or password")
#             return redirect("login")

#     return render(request, "login.html")


# # =========================
# # LOGOUT VIEW
# # =========================
# def logout_view(request):
#     logout(request)
#     return redirect("login")


# # =========================
# # DASHBOARD VIEW
# # =========================
# @login_required
# def dashboard_view(request):
#     recipes_with_score = []
#     user_input = ""

#     if request.method == "POST":
#         user_input = request.POST.get("ingredient", "")
#     elif request.method == "GET":
#         user_input = request.GET.get("ingredient", "")

#     if user_input:

#         # Save history only when manual search (POST)
#         if request.method == "POST":
#             SearchHistory.objects.create(
#                 user=request.user,
#                 ingredients=user_input
#             )

#         user_ingredients = [
#             i.strip().lower() for i in user_input.split(",")
#         ]

#         recipes = Recipe.objects.all()

#         for recipe in recipes:
#             recipe_ingredients = [
#                 i.strip().lower() for i in recipe.ingredients.split(",")
#             ]

#             matched = []
#             missing = []

#             for ingredient in recipe_ingredients:
#                 if ingredient in user_ingredients:
#                     matched.append(ingredient)
#                 else:
#                     missing.append(ingredient)

#             if len(matched) > 0:
#                 match_percentage = (
#                     len(matched) / len(recipe_ingredients)
#                 ) * 100 if len(recipe_ingredients) > 0 else 0

#                 recipes_with_score.append({
#                     "recipe": recipe,
#                     "match_percentage": round(match_percentage, 2),
#                     "missing": ", ".join(missing),
#                     "match_count": len(matched),
#                     "total_count": len(recipe_ingredients)
#                 })

#         recipes_with_score.sort(
#             key=lambda x: x["match_percentage"],
#             reverse=True
#         )

#         recipes_with_score = recipes_with_score[:5]

#     history = SearchHistory.objects.filter(
#         user=request.user
#     ).order_by("-searched_at")[:5]

#     return render(request, "dashboard.html", {
#         "recipes_with_score": recipes_with_score,
#         "history": history,
#         "user_input": user_input
#     })


# # =========================
# # DELETE SINGLE SEARCH HISTORY
# # =========================
# @login_required
# def delete_history(request, history_id):
#     history_item = get_object_or_404(
#         SearchHistory,
#         id=history_id,
#         user=request.user
#     )

#     history_item.delete()
#     messages.success(request, "Search deleted successfully ❌")

#     return redirect("dashboard")


# # =========================
# # 🔥 CLEAR ALL SEARCH HISTORY
# # =========================
# @login_required
# def clear_history(request):
#     if request.method == "POST":
#         SearchHistory.objects.filter(
#             user=request.user
#         ).delete()

#         messages.success(request, "All search history cleared 🗑️")

#     return redirect("dashboard")


# # =========================
# # RECIPE DETAIL VIEW
# # =========================
# @login_required
# def recipe_detail(request, id):
#     recipe = get_object_or_404(Recipe, id=id)

#     ingredients_list = [
#         i.strip() for i in recipe.ingredients.split(",")
#     ]

#     return render(request, "recipe_detail.html", {
#         "recipe": recipe,
#         "ingredients_list": ingredients_list
#     })



# # =========================
# # ADD FAVORITE VIEW
# # =========================
# @login_required
# def add_favorite(request, recipe_id):
#     recipe = get_object_or_404(Recipe, id=recipe_id)

#     Favorite.objects.get_or_create(
#         user=request.user,
#         recipe=recipe
#     )

#     messages.success(request, "Added to favorites ❤️")
#     return redirect("dashboard")


# # =========================
# # FAVORITE LIST VIEW
# # =========================
# @login_required
# def favorite_list(request):
#     favorites = Favorite.objects.filter(
#         user=request.user
#     )

#     return render(request, "favorites.html", {
#         "favorites": favorites
#     })


# # =========================
# # REMOVE FAVORITE VIEW
# # =========================
# @login_required
# def remove_favorite(request, recipe_id):
#     recipe = get_object_or_404(Recipe, id=recipe_id)

#     favorite = Favorite.objects.filter(
#         user=request.user,
#         recipe=recipe
#     )

#     if favorite.exists():
#         favorite.delete()
#         messages.success(request, "Removed from favorites ❌")

#     return redirect("favorites")
# # --------------------------------------------------------------------------------------------------

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Recipe, Favorite, SearchHistory


# =========================
# REGISTER VIEW
# =========================
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully")
        return redirect("login")

    return render(request, "register.html")


# =========================
# LOGIN VIEW
# =========================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    return render(request, "login.html")


# =========================
# LOGOUT VIEW
# =========================
def logout_view(request):
    logout(request)
    return redirect("login")


# =========================
# DASHBOARD VIEW
# =========================
@login_required
def dashboard_view(request):
    recipes_with_score = []
    user_input = ""

    if request.method == "POST":
        user_input = request.POST.get("ingredient", "")
    elif request.method == "GET":
        user_input = request.GET.get("ingredient", "")

    if user_input:

        # Save history only when manual search (POST)
        if request.method == "POST":
            SearchHistory.objects.create(
                user=request.user,
                ingredients=user_input
            )

        user_ingredients = [
            i.strip().lower() for i in user_input.split(",")
        ]

        recipes = Recipe.objects.all()

        for recipe in recipes:
            recipe_ingredients = [
                i.strip().lower() for i in recipe.ingredients.split(",")
            ]

            matched = []
            missing = []

            for ingredient in recipe_ingredients:
                if ingredient in user_ingredients:
                    matched.append(ingredient)
                else:
                    missing.append(ingredient)

            if len(matched) > 0:
                match_percentage = (
                    len(matched) / len(recipe_ingredients)
                ) * 100 if len(recipe_ingredients) > 0 else 0

                recipes_with_score.append({
                    "recipe": recipe,
                    "match_percentage": round(match_percentage, 2),
                    "missing": ", ".join(missing),
                    "match_count": len(matched),
                    "total_count": len(recipe_ingredients)
                })

        recipes_with_score.sort(
            key=lambda x: x["match_percentage"],
            reverse=True
        )

        recipes_with_score = recipes_with_score[:5]

    history = SearchHistory.objects.filter(
        user=request.user
    ).order_by("-searched_at")[:5]

    return render(request, "dashboard.html", {
        "recipes_with_score": recipes_with_score,
        "history": history,
        "user_input": user_input
    })


# =========================
# DELETE SINGLE SEARCH HISTORY
# =========================
@login_required
def delete_history(request, history_id):
    history_item = get_object_or_404(
        SearchHistory,
        id=history_id,
        user=request.user
    )

    history_item.delete()
    messages.success(request, "Search deleted successfully ❌")

    return redirect("dashboard")


# =========================
# 🔥 CLEAR ALL SEARCH HISTORY
# =========================
@login_required
def clear_history(request):
    if request.method == "POST":
        SearchHistory.objects.filter(
            user=request.user
        ).delete()

        messages.success(request, "All search history cleared 🗑️")

    return redirect("dashboard")


# =========================
# RECIPE DETAIL VIEW
# =========================
@login_required
def recipe_detail(request, id):

    recipe = get_object_or_404(Recipe, id=id)

    ingredients_list = [i.strip() for i in recipe.ingredients.split(",")]

    description_steps = [step.strip() for step in recipe.description.split(".") if step.strip()]

    return render(request, "recipe_detail.html", {
        "recipe": recipe,
        "ingredients_list": ingredients_list,
        "description_steps": description_steps
    })


# =========================
# ADD FAVORITE VIEW
# =========================
@login_required
def add_favorite(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    Favorite.objects.get_or_create(
        user=request.user,
        recipe=recipe
    )

    messages.success(request, "Added to favorites ❤️")
    return redirect("dashboard")


# =========================
# FAVORITE LIST VIEW
# =========================
@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(
        user=request.user
    )

    return render(request, "favorites.html", {
        "favorites": favorites
    })


# =========================
# REMOVE FAVORITE VIEW
# =========================
@login_required
def remove_favorite(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    favorite = Favorite.objects.filter(
        user=request.user,
        recipe=recipe
    )

    if favorite.exists():
        favorite.delete()
        messages.success(request, "Removed from favorites ❌")

    return redirect("favorites")
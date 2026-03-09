from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("recipe/<int:id>/", views.recipe_detail, name="recipe_detail"),

    # ❤️ ADD THIS LINE (IMPORTANT)
    path("favorite/<int:recipe_id>/", views.add_favorite, name="add_favorite"),
    path("favorites/",views.favorite_list,name="favorites"),
    path('remove-favorite/<int:recipe_id>/',views.remove_favorite,name='remove_favorite'),
    path('delete-history/<int:history_id>/',views.delete_history,name='delete_history'),
    path("clear-history/",views.clear_history,name="clear_history",)
]
# from django.db import models
# from django.contrib.auth.models import User


# class Recipe(models.Model):
#     name = models.CharField(max_length=100)
#     ingredients = models.TextField()
#     description = models.TextField()
#     cooking_time = models.CharField(max_length=50, default="15 minutes")
#     image = models.ImageField(upload_to='recipes/', null=True, blank=True)

#     def __str__(self):
#         return self.name


# class Favorite(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.user.username} - {self.recipe.name}"

# ----------------------------------------------------------------------------------


from django.db import models
from django.contrib.auth.models import User


class Recipe(models.Model):
    name = models.CharField(max_length=100)
    ingredients = models.TextField()
    description = models.TextField()
    cooking_time = models.CharField(max_length=50, default="15 minutes")
    image = models.ImageField(upload_to='recipes/', null=True, blank=True)

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.recipe.name}"


# 🔥 NEW MODEL ADDED
class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredients = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.ingredients}"
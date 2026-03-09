from app.services.recipe_service import get_recipe_service


def test_recipe_type_uses_ingredient_terms_not_title_substrings():
    service = get_recipe_service()
    assert service._classify_recipe_type(["eggplant", "tomato", "onion"]) == "veg"
    assert service._classify_recipe_type(["egg", "tomato", "onion"]) == "non-veg"
    assert service._classify_recipe_type(["chicken breast", "garlic", "onion"]) == "non-veg"

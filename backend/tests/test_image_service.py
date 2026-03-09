from app.services import recipe_image_service as image_service_module


def test_image_service_provider_priority_with_clip_validation(monkeypatch):
    service = image_service_module.RecipeImageService()
    service.fetch_enabled = True
    service.provider = "auto"
    service.spoonacular_key = "x"
    service.pexels_key = "x"
    service.unsplash_key = "x"

    service.get_image_for_recipe.cache_clear()

    monkeypatch.setattr(image_service_module, "get_cached_recipe_image", lambda _name: None)
    monkeypatch.setattr(image_service_module, "upsert_recipe_image_cache", lambda **_kwargs: True)

    monkeypatch.setattr(service, "_fetch_from_spoonacular", lambda _q: "https://bad.example/spoon.jpg")
    monkeypatch.setattr(service, "_fetch_from_pexels", lambda _q: "https://good.example/pexels.jpg")
    monkeypatch.setattr(service, "_fetch_from_unsplash", lambda _q: "https://backup.example/unsplash.jpg")

    class _Validator:
        loaded = True

        @staticmethod
        def validate_recipe_image(_name, image_url):
            return "good.example" in str(image_url)

    service._validator = _Validator()

    image_url, source = service.get_image_for_recipe("Tomato Soup", "veg")
    assert image_url == "https://good.example/pexels.jpg"
    assert source == "pexels"


def test_image_service_fallback_when_no_provider_result(monkeypatch):
    service = image_service_module.RecipeImageService()
    service.fetch_enabled = True
    service.provider = "auto"

    service.get_image_for_recipe.cache_clear()

    monkeypatch.setattr(image_service_module, "get_cached_recipe_image", lambda _name: None)
    monkeypatch.setattr(image_service_module, "upsert_recipe_image_cache", lambda **_kwargs: True)
    monkeypatch.setattr(service, "_fetch_and_verify", lambda _q, time_budget_sec=1.0: (None, None, False))
    monkeypatch.setattr(service, "enqueue_fetch", lambda _q: None)

    image_url, source = service.get_image_for_recipe("Chicken Curry", "non-veg")
    assert image_url.endswith("recipe_placeholder_nonveg.svg")
    assert source == "fallback"

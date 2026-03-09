from app.services.recipe_service import get_recipe_service


def test_recipe_ranking_includes_explanations():
    service = get_recipe_service()
    rows = service.recommend_recipes(
        query_terms=["tomato", "onion", "egg"],
        limit=3,
        term_weights={"tomato": 5, "onion": 4, "egg": 4},
    )
    assert isinstance(rows, list)
    assert rows

    first = rows[0]
    assert "recipe_name" in first
    assert "recipe_type" in first
    assert "cooking_time" in first
    assert "image_url" in first
    assert "matched_ingredients" in first
    assert "match_score" in first
    assert "ingredient_coverage" in first
    explanation = first.get("explanation") or {}
    assert "matched" in explanation
    assert "missing" in explanation
    assert "coverage" in explanation
    assert "ranking_score_components" in explanation

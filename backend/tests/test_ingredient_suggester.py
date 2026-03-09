from app.services.ingredient_suggester import get_ingredient_suggester


def test_ingredient_suggester_returns_related_items():
    suggester = get_ingredient_suggester()
    rows = suggester.suggest("egg", limit=5)
    assert isinstance(rows, list)
    if rows:
        first = rows[0]
        assert "ingredient" in first
        assert "score" in first


def test_ingredient_suggestion_endpoint(authed_client):
    response = authed_client.get("/api/ingredients/suggestions?ingredient=egg")
    assert response.status_code == 200
    payload = response.get_json() or {}
    assert payload.get("success") is True
    assert isinstance(payload.get("suggestions"), list)

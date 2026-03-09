def test_detect_pipeline_with_typed_ingredients(authed_client):
    response = authed_client.post("/api/detect", data={"ingredients": "tomato, onion, egg"})
    assert response.status_code == 200
    payload = response.get_json() or {}
    assert payload.get("success") is True
    assert isinstance(payload.get("recipes"), list)
    if payload.get("recipes"):
        first = payload["recipes"][0]
        assert "explanation" in first

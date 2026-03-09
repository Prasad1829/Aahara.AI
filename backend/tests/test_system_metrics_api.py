def test_system_metrics_endpoint(authed_client):
    # Trigger one detect call to populate timing metrics where available.
    authed_client.post("/api/detect", data={"ingredients": "tomato, egg"})

    response = authed_client.get("/api/admin/system-metrics")
    assert response.status_code == 200
    payload = response.get_json() or {}
    assert payload.get("success") is True
    assert isinstance(payload.get("metrics"), dict)


def test_system_status_endpoint(authed_client):
    response = authed_client.get("/api/admin/system-status")
    assert response.status_code == 200
    payload = response.get_json() or {}
    assert payload.get("success") is True
    assert "image_fetch_enabled" in payload
    assert "active_image_provider" in payload
    assert "embedding_model_loaded" in payload
    assert "clip_model_loaded" in payload
    assert "yolo_model_loaded" in payload

from app.ml import ingredient_detector as detector_module


class _FakeTensor:
    def __init__(self, value):
        self._value = value

    def item(self):
        return self._value


class _FakeBox:
    def __init__(self, conf, cls_idx):
        self.conf = [_FakeTensor(conf)]
        self.cls = [_FakeTensor(cls_idx)]


class _FakeResult:
    def __init__(self):
        self.names = {0: "tomato", 1: "eggplant", 2: "banana"}
        self.boxes = [
            _FakeBox(0.95, 0),
            _FakeBox(0.33, 1),  # below threshold -> ignored
            _FakeBox(0.64, 2),
        ]


class _FakeModel:
    def predict(self, source=None, verbose=False):
        return [_FakeResult()]


def test_yolo_detector_filters_low_confidence_and_normalizes(monkeypatch):
    monkeypatch.setattr(detector_module, "YOLO_MIN_CONFIDENCE", 0.4)

    detector = detector_module.IngredientDetector()
    detector.model = _FakeModel()
    detector.model_error = None
    detector._predict_cached.cache_clear()

    rows = detector.detect_ingredients("fake.jpg", top_k=5)
    names = [row.get("ingredient") for row in rows]

    assert "tomato" in names
    assert "banana" in names
    assert "eggplant" not in names

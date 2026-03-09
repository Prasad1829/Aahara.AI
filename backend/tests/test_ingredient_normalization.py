from app.ml.ingredient_normalizer import normalize_ingredient


def test_normalize_ingredient_aliases():
    assert normalize_ingredient("capsicum") == "bell pepper"
    assert normalize_ingredient("coriander") == "cilantro"
    assert normalize_ingredient("chilli") == "chili"
    assert normalize_ingredient("paneer") == "cottage cheese"
    assert normalize_ingredient("garbanzo") == "chickpea"

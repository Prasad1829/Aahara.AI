from app.ocr.ocr_engine import clean_ingredient_text


def test_ocr_cleaning_filters_and_corrects():
    items = clean_ingredient_text("Ingredients: tomto, capsicum, paneer, chilli powder, sugar")
    assert "tomato" in items
    assert "bell pepper" in items
    assert "cottage cheese" in items
    assert "chili" in items

import re

def clean_ocr_text(text):
    """
    Accepts either raw string or list.
    Returns cleaned list of words.
    """

    if not text:
        return []

    # If already list, join into string
    if isinstance(text, list):
        text = " ".join(text)

    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    words = text.split()
    words = [word.strip() for word in words if len(word) > 2]

    return words
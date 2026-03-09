import json
import os
import re
from functools import lru_cache

import cv2
import pytesseract

from app.ml.ingredient_normalizer import normalize_ingredient, normalize_ingredients_list


pytesseract.pytesseract.tesseract_cmd = os.getenv(
    "TESSERACT_CMD",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
)

DICTIONARY_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "ml", "config", "ingredient_dictionary.json")
)

OCR_STOPWORDS = {
    "ingredient",
    "ingredients",
    "contains",
    "contain",
    "may",
    "includes",
    "include",
    "water",
    "salt",
    "flavor",
    "natural",
    "artificial",
    "added",
    "less",
    "than",
    "and",
    "or",
    "with",
    "without",
    "for",
    "from",
    "the",
    "of",
}


@lru_cache(maxsize=1)
def _load_ingredient_dictionary():
    if not os.path.exists(DICTIONARY_PATH):
        return set()
    try:
        with open(DICTIONARY_PATH, "r", encoding="utf-8") as file_obj:
            words = json.load(file_obj) or []
        normalized = normalize_ingredients_list(words if isinstance(words, list) else [])
        return set(normalized)
    except Exception:
        return set()


def _preprocess_for_ocr(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.GaussianBlur(gray, (3, 3), 0)
    thresholded = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        3,
    )
    return thresholded


def extract_text_from_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise RuntimeError("Failed to load image for OCR")

    prepared = _preprocess_for_ocr(image)
    return pytesseract.image_to_string(prepared, config="--psm 6")


def _tokenize_text(text):
    cleaned = re.sub(r"[^a-zA-Z\s]", " ", str(text or "").lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return []
    return [token for token in cleaned.split(" ") if token]


def _levenshtein_distance(a, b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    previous = list(range(len(b) + 1))
    for i, char_a in enumerate(a, start=1):
        current = [i]
        for j, char_b in enumerate(b, start=1):
            insert_cost = current[j - 1] + 1
            delete_cost = previous[j] + 1
            replace_cost = previous[j - 1] + (0 if char_a == char_b else 1)
            current.append(min(insert_cost, delete_cost, replace_cost))
        previous = current
    return previous[-1]


def _correct_spelling(token, dictionary_terms):
    if not token or not dictionary_terms:
        return ""
    if token in dictionary_terms:
        return token
    if len(token) < 4:
        return ""

    best_term = ""
    best_distance = 99
    for term in dictionary_terms:
        if abs(len(term) - len(token)) > 3:
            continue
        if term and token and term[0] != token[0]:
            continue
        distance = _levenshtein_distance(token, term)
        if distance < best_distance:
            best_distance = distance
            best_term = term
            if distance == 1:
                break

    if best_distance <= 2:
        return best_term
    return ""


def clean_ingredient_text(text):
    dictionary_terms = _load_ingredient_dictionary()
    if not dictionary_terms:
        return []

    tokens = _tokenize_text(text)
    if not tokens:
        return []

    candidates = []
    # Capture phrase ingredients such as "olive oil".
    for index in range(len(tokens) - 1):
        phrase = normalize_ingredient(f"{tokens[index]} {tokens[index + 1]}")
        if phrase:
            candidates.append(phrase)

    for token in tokens:
        normalized = normalize_ingredient(token)
        if not normalized:
            continue
        if normalized in OCR_STOPWORDS:
            continue
        candidates.append(normalized)

    cleaned = []
    for item in candidates:
        if item in dictionary_terms:
            cleaned.append(item)
            continue

        if " " in item:
            # Avoid correcting multi-word phrases to unrelated terms.
            continue

        corrected = _correct_spelling(item, dictionary_terms)
        if corrected and corrected not in OCR_STOPWORDS:
            cleaned.append(corrected)

    return normalize_ingredients_list(cleaned)


def extract_ingredients_from_image(image_path):
    raw_text = extract_text_from_image(image_path)
    return clean_ingredient_text(raw_text)

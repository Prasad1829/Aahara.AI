import math

import cv2
import numpy as np

from app.services.cnn_preprocessing import crop_largest_ingredient_region


def detect_onion_heuristic(image_path: str) -> dict | None:
    image = cv2.imread(image_path)
    if image is None:
        return None

    image = crop_largest_ingredient_region(image)
    if image is None or image.size == 0:
        return None

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Red onion tends to appear in red-magenta-purple bands in HSV.
    lower_red_1 = np.array([0, 50, 40], dtype=np.uint8)
    upper_red_1 = np.array([12, 255, 255], dtype=np.uint8)
    lower_red_2 = np.array([160, 50, 40], dtype=np.uint8)
    upper_red_2 = np.array([179, 255, 255], dtype=np.uint8)
    lower_purple = np.array([120, 40, 35], dtype=np.uint8)
    upper_purple = np.array([170, 255, 255], dtype=np.uint8)

    mask = (
        cv2.inRange(hsv, lower_red_1, upper_red_1)
        | cv2.inRange(hsv, lower_red_2, upper_red_2)
        | cv2.inRange(hsv, lower_purple, upper_purple)
    )

    purple_ratio = float(np.count_nonzero(mask)) / float(mask.size)
    if purple_ratio < 0.12:
        return None

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)
    if area <= 0:
        return None

    perimeter = cv2.arcLength(largest, True)
    if perimeter <= 0:
        return None

    circularity = float((4.0 * math.pi * area) / (perimeter * perimeter))
    x, y, w, h = cv2.boundingRect(largest)
    aspect_ratio = float(w) / float(h) if h else 0.0

    # Onion bulbs are typically near-round with a strong red/purple surface.
    if circularity >= 0.28 and 0.65 <= aspect_ratio <= 1.35:
        confidence = min(0.98, round(0.65 + purple_ratio + max(0.0, circularity - 0.28), 2))
        return {
            "ingredient": "onion",
            "confidence": confidence,
            "top_predictions": [
                {"ingredient": "onion", "confidence": confidence},
            ],
        }

    return None

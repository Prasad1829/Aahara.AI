"""
Download one real reference image per ingredient class from Wikipedia.

This script uses the Wikipedia summary API to fetch each article's lead image
and stores it inside the matching dataset class folder as `wiki_<class>.jpg`.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


BASE_DIR = pathlib.Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset"
USER_AGENT = "AaharaAI-DatasetUpdater/1.0"


ARTICLE_MAP = {
    "cabbage": "Cabbage",
    "capsicum": "Bell_pepper",
    "carrot": "Carrot",
    "cauliflower": "Cauliflower",
    "chicken": "Chicken_as_food",
    "cucumber": "Cucumber",
    "egg": "Egg_as_food",
    "eggplant": "Eggplant",
    "fish": "Fish_as_food",
    "garlic": "Garlic",
    "ginger": "Ginger",
    "lemon": "Lemon",
    "okra": "Okra",
    "onion": "Onion",
    "paneer": "Paneer",
    "peas": "Pea",
    "potato": "Potato",
    "rice": "Rice",
    "spinach": "Spinach",
    "tomato": "Tomato",
}


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def download_file(url: str, destination: pathlib.Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp, destination.open("wb") as fh:
        fh.write(resp.read())


def summary_url(title: str) -> str:
    encoded = urllib.parse.quote(title, safe="")
    return f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"


def image_url_from_summary(summary: dict) -> str | None:
    thumbnail = summary.get("thumbnail", {})
    if thumbnail.get("source"):
        return thumbnail["source"]
    original = summary.get("originalimage", {})
    if original.get("source"):
        return original["source"]
    return None


def main() -> int:
    requested_classes = set(sys.argv[1:]) if len(sys.argv) > 1 else None
    failures: list[str] = []

    for class_name, article_title in ARTICLE_MAP.items():
        if requested_classes and class_name not in requested_classes:
            continue
        class_dir = DATASET_DIR / class_name
        if not class_dir.exists():
            failures.append(f"{class_name}: missing folder")
            continue

        try:
            summary = fetch_json(summary_url(article_title))
            image_url = image_url_from_summary(summary)
            if not image_url:
                failures.append(f"{class_name}: no image in article")
                continue

            ext = pathlib.Path(urllib.parse.urlparse(image_url).path).suffix or ".jpg"
            destination = class_dir / f"wiki_{class_name}{ext}"
            download_file(image_url, destination)
            print(f"saved {class_name} -> {destination.name}")
            time.sleep(1.5)
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            failures.append(f"{class_name}: {exc}")

    if failures:
        print("\nfailures:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("\nall class images downloaded successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

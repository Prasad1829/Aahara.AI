import argparse
import ast
import csv
import json
import os
import re


def _normalize_text(value):
    return re.sub(r"\s+", " ", str(value or "").strip())


def _choose_column(fieldnames, candidates):
    lowered = {name.lower(): name for name in fieldnames}
    for candidate in candidates:
        if candidate in lowered:
            return lowered[candidate]
    return None


def _parse_list_like(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [_normalize_text(item) for item in value if _normalize_text(item)]

    text = str(value).strip()
    if not text:
        return []

    # Try JSON / Python list string
    for parser in (json.loads, ast.literal_eval):
        try:
            parsed = parser(text)
            if isinstance(parsed, list):
                cleaned = [_normalize_text(item) for item in parsed if _normalize_text(item)]
                if cleaned:
                    return cleaned
        except Exception:
            pass

    # Fallback: split by common separators
    if "\n" in text:
        parts = text.splitlines()
    elif "|" in text:
        parts = text.split("|")
    elif ";" in text:
        parts = text.split(";")
    else:
        parts = text.split(",")
    return [_normalize_text(item) for item in parts if _normalize_text(item)]


def build_dataset(input_csv, output_json, id_start=2000000):
    with open(input_csv, "r", encoding="utf-8", newline="") as file_obj:
        reader = csv.DictReader(file_obj)
        fieldnames = reader.fieldnames or []
        if not fieldnames:
            raise ValueError("CSV has no header row.")

        name_col = _choose_column(
            fieldnames,
            [
                "name",
                "title",
                "recipe_name",
                "recipe",
                "dish_name",
                "translatedrecipename",
                "translated_recipe_name",
            ],
        )
        ingredients_col = _choose_column(
            fieldnames,
            [
                "ingredients",
                "ingredient_list",
                "ingredient",
                "cleaned_ingredients",
                "translatedingredients",
                "translated_ingredients",
                "cleaned-ingredients",
            ],
        )
        instructions_col = _choose_column(
            fieldnames,
            [
                "instructions",
                "directions",
                "steps",
                "method",
                "recipe_instructions",
                "translatedinstructions",
                "translated_instructions",
            ],
        )
        image_col = _choose_column(
            fieldnames,
            ["image_url", "image-url", "image", "photo_url", "thumbnail"],
        )

        if not name_col or not ingredients_col or not instructions_col:
            raise ValueError(
                "Could not detect required columns. Need name/title + ingredients + instructions."
            )

        normalized = []
        next_id = int(id_start)

        for row in reader:
            name = _normalize_text(row.get(name_col))
            ingredients = _parse_list_like(row.get(ingredients_col))
            instructions = _parse_list_like(row.get(instructions_col))

            if not name or not ingredients or not instructions:
                continue

            recipe_row = {
                "id": next_id,
                "name": name,
                "ingredients": ingredients,
                "instructions": instructions,
            }

            if image_col:
                image_url = _normalize_text(row.get(image_col))
                if image_url:
                    recipe_row["image_url"] = image_url

            normalized.append(recipe_row)
            next_id += 1

    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as file_obj:
        json.dump(normalized, file_obj, ensure_ascii=False)

    return len(normalized)


def main():
    parser = argparse.ArgumentParser(
        description="Convert recipe CSV to app-ready normalized JSON."
    )
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON file path (e.g., dataset/processed/recipes/indian_recipes_normalized.json)",
    )
    parser.add_argument(
        "--id-start",
        type=int,
        default=2000000,
        help="Starting recipe ID for generated records",
    )
    args = parser.parse_args()

    total = build_dataset(args.input, args.output, id_start=args.id_start)
    print(f"[OK] Wrote {total} recipes -> {args.output}")


if __name__ == "__main__":
    main()

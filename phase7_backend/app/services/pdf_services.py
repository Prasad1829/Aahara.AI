
import os
import re
import pdfplumber

# ─────────────────────────────────────────────
# KNOWN INGREDIENTS LIST (your 19 classes)
# ─────────────────────────────────────────────
KNOWN_INGREDIENTS = [
    "cabbage", "capsicum", "carrot", "cauliflower", "chicken",
    "cucumber", "egg", "eggplant", "fish", "garlic", "ginger",
    "okra", "onion", "paneer", "peas", "potato", "rice",
    "spinach", "tomato"
]

# Common recipe section headers
INGREDIENT_HEADERS = [
    "ingredients", "ingredient list", "you will need",
    "what you need", "items needed", "materials"
]

# Words to skip (not ingredients)
SKIP_WORDS = [
    "instructions", "directions", "method", "steps", "procedure",
    "notes", "tips", "serving", "serves", "preparation", "prep",
    "cook", "total", "time", "minutes", "hours", "calories"
]


# ─────────────────────────────────────────────
# CORE EXTRACTION FUNCTIONS
# ─────────────────────────────────────────────

def clean_line(line: str) -> str:
    """Clean a line of text"""
    line = line.strip()
    line = re.sub(r'[•\-\*\→\►]', '', line)   # Remove bullets
    line = re.sub(r'\s+', ' ', line)             # Collapse spaces
    line = re.sub(r'^\d+[\.\)]\s*', '', line)    # Remove numbered list prefix
    return line.strip()


def is_ingredient_line(line: str) -> bool:
    """Check if a line looks like an ingredient"""
    line_lower = line.lower()

    # Skip empty lines
    if not line:
        return False

    # Skip lines that are section headers
    for skip in SKIP_WORDS:
        if line_lower.startswith(skip):
            return False

    # Skip very long lines (probably instructions not ingredients)
    if len(line) > 100:
        return False

    # Skip lines with no letters
    if not re.search(r'[a-zA-Z]', line):
        return False

    return True


def extract_known_ingredients(text: str) -> list:
    """Find known ingredients from KNOWN_INGREDIENTS list in text"""
    found = []
    text_lower = text.lower()
    for ingredient in KNOWN_INGREDIENTS:
        if ingredient in text_lower:
            if ingredient not in found:
                found.append(ingredient)
    return found


def extract_ingredients_section(lines: list) -> list:
    """Extract lines from the ingredients section of a recipe"""
    ingredients = []
    in_ingredients_section = False

    for line in lines:
        line_clean = clean_line(line)
        line_lower = line_clean.lower()

        # Detect start of ingredients section
        if any(header in line_lower for header in INGREDIENT_HEADERS):
            in_ingredients_section = True
            continue

        # Detect end of ingredients section
        if in_ingredients_section:
            if any(skip in line_lower for skip in ["instruction", "direction", "method", "step", "procedure"]):
                in_ingredients_section = False
                continue

            if is_ingredient_line(line_clean):
                ingredients.append(line_clean)

    return ingredients


def extract_ingredients_from_pdf(pdf_path: str) -> dict:
    """
    Main function — Extract ingredients from a PDF recipe file

    Returns:
        {
            "status": "success" or "error",
            "pdf_file": "filename.pdf",
            "total_pages": 3,
            "raw_text": "full extracted text...",
            "ingredient_lines": ["2 cups flour", "1 tsp salt", ...],
            "known_ingredients": ["tomato", "onion", ...],
            "message": "Found 5 ingredients"
        }
    """
    if not os.path.exists(pdf_path):
        return {
            "status": "error",
            "message": f"PDF file not found: {pdf_path}",
            "pdf_file": pdf_path
        }

    try:
        all_text = ""
        all_lines = []
        total_pages = 0

        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"  📄 PDF opened: {total_pages} pages found")

            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    all_text += text + "\n"
                    lines = text.split("\n")
                    all_lines.extend(lines)
                    print(f"  📖 Page {page_num}: {len(lines)} lines extracted")

        if not all_text.strip():
            return {
                "status": "error",
                "message": "No text found in PDF. It may be a scanned image PDF.",
                "pdf_file": os.path.basename(pdf_path),
                "total_pages": total_pages
            }

        # Extract ingredient section lines
        ingredient_lines = extract_ingredients_section(all_lines)

        # Extract known ingredients from full text
        known_ingredients = extract_known_ingredients(all_text)

        # If no section found, try extracting known ingredients directly
        if not ingredient_lines and known_ingredients:
            ingredient_lines = known_ingredients

        return {
            "status": "success",
            "pdf_file": os.path.basename(pdf_path),
            "total_pages": total_pages,
            "raw_text": all_text[:500] + "..." if len(all_text) > 500 else all_text,
            "ingredient_lines": ingredient_lines,
            "known_ingredients": known_ingredients,
            "message": f"Found {len(known_ingredients)} known ingredients and {len(ingredient_lines)} ingredient lines"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading PDF: {str(e)}",
            "pdf_file": os.path.basename(pdf_path)
        }


# ─────────────────────────────────────────────
# RUN DIRECTLY FOR TESTING
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "sample_recipe.pdf"

    print("=" * 50)
    print("  AHARA AI — PDF Extraction Service")
    print("=" * 50)
    print(f"\n🔍 Processing: {pdf_path}\n")

    result = extract_ingredients_from_pdf(pdf_path)

    print("\n" + "=" * 50)
    print("  RESULTS")
    print("=" * 50)
    print(f"  Status        : {result['status']}")
    print(f"  PDF File      : {result.get('pdf_file', 'N/A')}")
    print(f"  Total Pages   : {result.get('total_pages', 'N/A')}")
    print(f"  Message       : {result.get('message', 'N/A')}")

    if result['status'] == 'success':
        print(f"\n  📋 Ingredient Lines Found ({len(result['ingredient_lines'])}):")
        for line in result['ingredient_lines']:
            print(f"     - {line}")

        print(f"\n  ✅ Known Ingredients Matched ({len(result['known_ingredients'])}):")
        for ing in result['known_ingredients']:
            print(f"     🥦 {ing}")

    print("=" * 50)
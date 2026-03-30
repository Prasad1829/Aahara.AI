from fpdf import FPDF

def create_sample_recipe_pdf():
    pdf = FPDF()
    pdf.add_page()

    # ─────────────────────────────────────────────
    # TITLE
    # ─────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", size=20)
    pdf.cell(0, 12, "Aloo Matar (Potato & Peas Curry)", 
             new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(3)

    pdf.set_font("Helvetica", "I", size=11)
    pdf.cell(0, 8, "A classic Indian vegetarian recipe", 
             new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    # ─────────────────────────────────────────────
    # RECIPE INFO
    # ─────────────────────────────────────────────
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 7, "Prep Time: 15 minutes  |  Cook Time: 30 minutes  |  Serves: 4",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # ─────────────────────────────────────────────
    # INGREDIENTS SECTION
    # ─────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", size=14)
    pdf.cell(0, 10, "Ingredients", new_x="LMARGIN", new_y="NEXT")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    pdf.set_font("Helvetica", size=11)

    ingredients = [
        "- 3 medium potato, peeled and cubed",
        "- 1 cup peas (fresh or frozen)",
        "- 2 medium tomato, chopped",
        "- 1 large onion, finely chopped",
        "- 4 cloves garlic, minced",
        "- 1 inch ginger, freshly grated",
        "- 1 cup spinach leaves (optional)",
        "- 2 tbsp oil",
        "- 1 tsp cumin seeds",
        "- 1 tsp turmeric powder",
        "- 1 tsp red chili powder",
        "- 1 tsp garam masala",
        "- Salt to taste",
        "- Fresh carrot slices for garnish (optional)",
    ]

    for item in ingredients:
        pdf.cell(0, 8, item, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)

    # ─────────────────────────────────────────────
    # INSTRUCTIONS SECTION
    # ─────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", size=14)
    pdf.cell(0, 10, "Instructions", new_x="LMARGIN", new_y="NEXT")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    pdf.set_font("Helvetica", size=11)

    steps = [
        "1. Heat oil in a large pan over medium heat.",
        "2. Add cumin seeds and let them splutter for 30 seconds.",
        "3. Add onion and saute until golden brown, about 5 minutes.",
        "4. Add garlic and ginger, cook for 2 minutes until fragrant.",
        "5. Add chopped tomatoes and cook until they turn soft and mushy.",
        "6. Add turmeric, chili powder and garam masala. Mix well.",
        "7. Add cubed potato and peas. Stir to coat with the masala.",
        "8. Pour in 1/2 cup water, cover and cook for 15-20 minutes.",
        "9. Check potato is cooked through with a fork.",
        "10. Add spinach leaves and stir for 2 minutes.",
        "11. Season with salt and serve hot with rice or roti.",
    ]

    for step in steps:
        pdf.multi_cell(0, 8, step, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)

    # ─────────────────────────────────────────────
    # TIPS SECTION
    # ─────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", size=14)
    pdf.cell(0, 10, "Tips", new_x="LMARGIN", new_y="NEXT")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    pdf.set_font("Helvetica", size=11)
    tips = [
        "- For extra protein, add paneer cubes in the last 5 minutes.",
        "- You can also add cauliflower or capsicum for variation.",
        "- Store leftovers in the fridge for up to 3 days.",
    ]

    for tip in tips:
        pdf.cell(0, 8, tip, new_x="LMARGIN", new_y="NEXT")

    # Save PDF
    output_path = "P:/INFOSYS PROJECT/phase7_backend/sample_recipe.pdf"
    pdf.output(output_path)
    print(f"✅ Sample recipe PDF created: {output_path}")
    print("📄 Contains these AHARA AI ingredients:")
    print("   potato, peas, tomato, onion, garlic, ginger, spinach, carrot, paneer, cauliflower, capsicum")


if __name__ == "__main__":
    create_sample_recipe_pdf()

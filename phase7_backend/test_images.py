"""
Test that different recipes get different images
"""
from app.services.image_service import get_recipe_image

print("Testing Image Fetching for Different Recipes")
print("=" * 70)
print()

recipes = ["Chicken Masala", "Butter Chicken", "Chicken Do Pyaza", "Aloo Gobi", "Paneer Butter Masala"]

images_fetched = {}

for recipe in recipes:
    print(f"Fetching image for: {recipe}")
    image_url = get_recipe_image(recipe)
    images_fetched[recipe] = image_url
    
    # Show shortened URL for readability
    if "unsplash" in image_url.lower():
        short_id = image_url.split('/')[-1].split('?')[0][:10]
        print(f"  ✓ Got image ID: {short_id}...")
    else:
        print(f"  ✓ {image_url[:60]}...")
    print()

# Check uniqueness
unique_images = set(images_fetched.values())
print(f"Summary:")
print(f"  Total recipes: {len(recipes)}")
print(f"  Unique images: {len(unique_images)}")

if len(unique_images) == len(recipes):
    print("  ✓ All recipes have different images!")
elif len(unique_images) > 1:
    print(f"  ⚠ Some recipes share images (but at least {len(unique_images)} are different)")
else:
    print("  ✗ All recipes have the same image")

print()
for recipe, image in images_fetched.items():
    short_id = image.split('/')[-1].split('?')[0][:15] if "unsplash" in image else "fallback"
    print(f"{recipe:25} -> {short_id}")

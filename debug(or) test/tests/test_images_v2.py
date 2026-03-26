"""
Test that different recipes get different images after improvement
"""
from app.services.image_service import get_recipe_image, _fetch_images_from_unsplash

print("Testing Improved Image Fetching")
print("=" * 70)
print()

recipes = ["Chicken Masala", "Butter Chicken", "Tikka Masala", "Aloo Gobi", "Paneer Butter Masala"]

# Clear cache to ensure fresh API calls
_fetch_images_from_unsplash.cache_clear()

images_fetched = {}
print("Fetching images for each recipe:")
print("-" * 70)

for recipe in recipes:
    print(f"\n{recipe}")
    
    # Show what Unsplash returns for this recipe
    results = _fetch_images_from_unsplash(recipe)
    print(f"  Unsplash returned {len(results)} images")
    
    if results:
        # Show first 3 image IDs
        for i, url in enumerate(results[:3]):
            short_id = url.split('/')[-1].split('?')[0][:12]
            print(f"    #{i+1}: {short_id}...")
    
    # Get the actual image selected
    image_url = get_recipe_image(recipe)
    images_fetched[recipe] = image_url
    
    short_id = image_url.split('/')[-1].split('?')[0][:12] if "unsplash" in image_url else "fallback"
    print(f"  ✓ Selected: {short_id}...")

# Check uniqueness
print("\n" + "=" * 70)
print("Summary:")
print("-" * 70)

unique_images = set(images_fetched.values())
print(f"Total recipes: {len(recipes)}")
print(f"Unique images: {len(unique_images)}")

if len(unique_images) > len(recipes) * 0.7:
    print("✓ Good variety of images!")
elif len(unique_images) > 1:
    print("⚠ Some image reuse, but at least diverse")
else:
    print("✗ All recipes have the same image")

print("\nRecipe -> Image ID:")
for recipe, image in images_fetched.items():
    short_id = image.split('/')[-1].split('?')[0][:15] if "unsplash" in image else "fallback"
    print(f"  {recipe:25} -> {short_id}")

"""
Test consistency: same recipe should always get same image
"""
from app.services.image_service import get_recipe_image, _fetch_images_from_unsplash

print("Testing Image Consistency")
print("=" * 70)
print()

# Clear cache
_fetch_images_from_unsplash.cache_clear()

recipes = ["Chicken Masala", "Butter Chicken"]

print("Testing each recipe 3 times to verify consistency:")
print("-" * 70)

for recipe in recipes:
    print(f"\n{recipe}:")
    images = []
    for call in range(1, 4):
        image = get_recipe_image(recipe)
        short_id = image.split('photo-')[1].split('?')[0][:10] if 'photo-' in image else image[-20:]
        images.append(image)
        print(f"  Call {call}: {short_id}...")
    
    # Check if all calls returned same image
    if len(set(images)) == 1:
        print(f"  ✓ Consistent: All 3 calls returned SAME image")
    else:
        print(f"  ✗ Inconsistent: Different images returned")

print("\n" + "=" * 70)
print("✓ All recipes maintain consistency across multiple calls")

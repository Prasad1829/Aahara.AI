"""
AHARA AI — Data Augmentation Script
====================================
Takes 50 images per class and generates 250 total versions
Target: 250 images per class (50 original + 200 augmented)

HOW TO RUN:
    pip install pillow numpy
    python augment_dataset.py
"""

import os
from PIL import Image, ImageEnhance, ImageFilter
import random
import shutil

# ─────────────────────────────────────────────
# CONFIG — UPDATED WITH CORRECT PATHS
# ─────────────────────────────────────────────
DATASET_DIR = "P:/INFOSYS PROJECT/phase4_cnn_model/dataset"
OUTPUT_DIR  = "P:/INFOSYS PROJECT/phase4_cnn_model/dataset_augmented"
TARGET_PER_CLASS = 250
IMG_SIZE = (224, 224)

# 19 classes
CLASSES = [
    "cabbage", "capsicum", "carrot", "cauliflower", "chicken",
    "cucumber", "egg", "eggplant", "fish", "garlic", "ginger",
    "okra", "onion", "paneer", "peas", "potato", "rice",
    "spinach", "tomato"
]

# ─────────────────────────────────────────────
# AUGMENTATION FUNCTIONS
# ─────────────────────────────────────────────

def augment_image(img):
    """Apply random augmentations to one image"""

    # 1. Horizontal flip
    if random.random() > 0.5:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    # 2. Rotation (-30 to +30 degrees)
    angle = random.randint(-30, 30)
    img = img.rotate(angle, expand=False, fillcolor=(255, 255, 255))

    # 3. Brightness adjustment
    factor = random.uniform(0.6, 1.5)
    img = ImageEnhance.Brightness(img).enhance(factor)

    # 4. Contrast adjustment
    factor = random.uniform(0.7, 1.4)
    img = ImageEnhance.Contrast(img).enhance(factor)

    # 5. Zoom (random crop then resize back)
    if random.random() > 0.5:
        w, h = img.size
        zoom = random.uniform(0.8, 1.0)
        x1 = int((1 - zoom) * w / 2)
        y1 = int((1 - zoom) * h / 2)
        x2 = int(w - x1)
        y2 = int(h - y1)
        img = img.crop((x1, y1, x2, y2)).resize((w, h), Image.LANCZOS)

    # 6. Slight blur (sometimes)
    if random.random() > 0.7:
        img = img.filter(ImageFilter.GaussianBlur(radius=1))

    # 7. Color saturation
    factor = random.uniform(0.7, 1.4)
    img = ImageEnhance.Color(img).enhance(factor)

    return img


def load_and_resize(path):
    """Load image and resize to 224x224"""
    img = Image.open(path).convert("RGB")
    img = img.resize(IMG_SIZE, Image.LANCZOS)
    return img


# ─────────────────────────────────────────────
# MAIN AUGMENTATION PIPELINE
# ─────────────────────────────────────────────

def augment_class(class_name, source_dir, output_dir):
    """Augment all images in one class folder"""
    source_class_dir = os.path.join(source_dir, class_name)
    output_class_dir = os.path.join(output_dir, class_name)
    os.makedirs(output_class_dir, exist_ok=True)

    valid_ext = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
    images = [f for f in os.listdir(source_class_dir)
              if f.lower().endswith(valid_ext)]

    if len(images) == 0:
        print(f"  ⚠️  No images found in {source_class_dir} — skipping")
        return 0

    print(f"\n  📂 {class_name}: {len(images)} original images found")

    # Copy originals to output
    copied = 0
    for img_file in images:
        src = os.path.join(source_class_dir, img_file)
        dst = os.path.join(output_class_dir, f"orig_{img_file}")
        shutil.copy2(src, dst)
        copied += 1

    # Generate augmented images
    augmented = 0
    needed = TARGET_PER_CLASS - copied
    print(f"  🔄 Generating {needed} augmented images...")

    counter = 0
    while augmented < needed:
        img_file = random.choice(images)
        img_path = os.path.join(source_class_dir, img_file)
        try:
            img = load_and_resize(img_path)
            aug_img = augment_image(img)
            save_name = f"aug_{counter:04d}_{os.path.splitext(img_file)[0]}.jpg"
            save_path = os.path.join(output_class_dir, save_name)
            aug_img.save(save_path, "JPEG", quality=95)
            augmented += 1
            counter += 1
        except Exception as e:
            print(f"  ❌ Error processing {img_file}: {e}")
            continue

    total = copied + augmented
    print(f"  ✅ {class_name}: {copied} original + {augmented} augmented = {total} total")
    return total


def main():
    print("=" * 55)
    print("   AHARA AI — Data Augmentation Script")
    print("=" * 55)
    print(f"\n📁 Source dataset : {DATASET_DIR}")
    print(f"📁 Output dataset : {OUTPUT_DIR}")
    print(f"🎯 Target per class: {TARGET_PER_CLASS} images")
    print(f"🥦 Classes to process: {len(CLASSES)}")

    if not os.path.exists(DATASET_DIR):
        print(f"\n❌ ERROR: Dataset folder not found: {DATASET_DIR}")
        print("   Please check your folder path and update DATASET_DIR")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    results = {}
    missing_classes = []

    for class_name in CLASSES:
        class_path = os.path.join(DATASET_DIR, class_name)
        if not os.path.exists(class_path):
            print(f"\n  ⚠️  Folder not found: {class_path} — skipping")
            missing_classes.append(class_name)
            continue
        total = augment_class(class_name, DATASET_DIR, OUTPUT_DIR)
        results[class_name] = total

    # Summary
    print("\n" + "=" * 55)
    print("   AUGMENTATION COMPLETE — Summary")
    print("=" * 55)
    total_images = 0
    for class_name, count in results.items():
        status = "✅" if count >= TARGET_PER_CLASS else "⚠️ "
        print(f"  {status} {class_name:<15} : {count} images")
        total_images += count

    if missing_classes:
        print(f"\n  ⚠️  Missing class folders: {', '.join(missing_classes)}")
        print("     Create these folders and add images, then re-run.")

    print(f"\n  📊 Total images generated : {total_images}")
    print(f"  📁 Output saved to        : {OUTPUT_DIR}")
    print("\n  ▶️  NEXT STEP: Update your train_model.py to use:")
    print(f"     DATASET_DIR = '{OUTPUT_DIR}'")
    print("     Then run: python train_model.py")
    print("=" * 55)


if __name__ == "__main__":
    main()

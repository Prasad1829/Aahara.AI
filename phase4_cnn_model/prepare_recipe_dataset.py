import argparse
import os
import shutil
from pathlib import Path


ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}

# Canonical recipe classes we want for this project.
TARGET_CLASSES = [
    "cabbage",
    "capsicum",
    "carrot",
    "cauliflower",
    "chicken",
    "cucumber",
    "egg",
    "eggplant",
    "fish",
    "garlic",
    "ginger",
    "okra",
    "onion",
    "paneer",
    "peas",
    "potato",
    "rice",
    "spinach",
    "tomato",
]

# Normalize source folder names to target class names.
ALIASES = {
    "bell pepper": "capsicum",
    "chilli pepper": "capsicum",
    "jalepeno": "capsicum",
    "jalapeno": "capsicum",
    "green chilli": "capsicum",
    "green chili": "capsicum",
    "brinjal": "eggplant",
    "ladyfinger": "okra",
    "lady_finger": "okra",
    "bhindi": "okra",
    "soy beans": "peas",
    "soy_beans": "peas",
}


def normalize_name(name: str) -> str:
    base = name.strip().lower().replace("_", " ")
    if base in ALIASES:
        return ALIASES[base]
    return base.replace(" ", "_") if base in {"soy beans"} else base


def find_class_dirs(source_root: Path):
    """
    Accept both structures:
    1) dataset/<class>/*
    2) dataset/train/<class>/* + dataset/test/<class>/* + dataset/validation/<class>/*
    """
    split_names = {"train", "test", "validation", "val"}
    direct_children = [p for p in source_root.iterdir() if p.is_dir()]
    if direct_children and all(p.name.lower() in split_names for p in direct_children):
        class_dirs = []
        for split_dir in direct_children:
            for cls in split_dir.iterdir():
                if cls.is_dir():
                    class_dirs.append(cls)
        return class_dirs
    return direct_children


def prepare_dataset(source_dir: Path, target_dir: Path):
    if not source_dir.exists():
        raise FileNotFoundError(f"Source dataset not found: {source_dir}")

    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    for cls in TARGET_CLASSES:
        (target_dir / cls).mkdir(parents=True, exist_ok=True)

    copied_counts = {cls: 0 for cls in TARGET_CLASSES}
    skipped_folders = []

    class_dirs = find_class_dirs(source_dir)

    for src_class_dir in class_dirs:
        normalized = normalize_name(src_class_dir.name)
        # Map alias after generic normalization.
        normalized = ALIASES.get(normalized, normalized)
        if normalized not in TARGET_CLASSES:
            skipped_folders.append(src_class_dir.name)
            continue

        out_dir = target_dir / normalized
        for f in src_class_dir.rglob("*"):
            if not f.is_file():
                continue
            if f.suffix.lower() not in ALLOWED_EXTS:
                continue
            dest_name = f"{src_class_dir.name}_{copied_counts[normalized]}{f.suffix.lower()}"
            shutil.copy2(f, out_dir / dest_name)
            copied_counts[normalized] += 1

    print("Prepared dataset:", target_dir)
    print("\nCopied image counts:")
    for cls in TARGET_CLASSES:
        print(f"  {cls}: {copied_counts[cls]}")

    print("\nSkipped source folders (not in target classes):")
    if skipped_folders:
        for name in sorted(set(skipped_folders)):
            print(f"  - {name}")
    else:
        print("  (none)")

    empty = [k for k, v in copied_counts.items() if v == 0]
    if empty:
        print("\nWARNING: These classes have 0 images:")
        for cls in empty:
            print(f"  - {cls}")
    else:
        print("\nAll target classes have at least 1 image.")


def parse_args():
    parser = argparse.ArgumentParser(description="Prepare filtered recipe dataset for training.")
    parser.add_argument(
        "--source-dir",
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dataset")),
        help="Source dataset root path.",
    )
    parser.add_argument(
        "--target-dir",
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dataset_recipe")),
        help="Target filtered dataset root path.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    prepare_dataset(Path(args.source_dir), Path(args.target_dir))


if __name__ == "__main__":
    main()

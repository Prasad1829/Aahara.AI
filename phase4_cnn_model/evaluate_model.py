import argparse
import json
import os
from pathlib import Path

import numpy as np
import tensorflow as tf


ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}


def load_class_names(path: Path):
    with path.open("r", encoding="utf-8") as f:
        class_names = json.load(f)
    if not isinstance(class_names, list) or not class_names:
        raise ValueError(f"Invalid class names file: {path}")
    return class_names


def collect_images(dataset_dir: Path, class_names, validation_split, seed):
    rng = np.random.default_rng(seed)
    image_paths = []
    labels = []
    counts = {}

    for label, class_name in enumerate(class_names):
        class_dir = dataset_dir / class_name
        if not class_dir.is_dir():
            counts[class_name] = 0
            continue

        files = sorted(
            p for p in class_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in ALLOWED_EXTS
        )
        counts[class_name] = len(files)
        if not files:
            continue

        indices = np.arange(len(files))
        rng.shuffle(indices)
        val_count = max(1, int(len(files) * validation_split))
        val_indices = sorted(indices[:val_count])

        for idx in val_indices:
            image_paths.append(str(files[int(idx)]))
            labels.append(label)

    return image_paths, np.array(labels, dtype=np.int64), counts


def make_dataset(image_paths, labels, img_size, batch_size):
    paths_ds = tf.data.Dataset.from_tensor_slices((image_paths, labels))

    def load_image(path, label):
        image = tf.io.read_file(path)
        image = tf.io.decode_image(image, channels=3, expand_animations=False)
        image = tf.image.resize(image, [img_size, img_size])
        image = tf.cast(image, tf.float32)
        return image, label

    return (
        paths_ds
        .map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
        .batch(batch_size)
        .prefetch(tf.data.AUTOTUNE)
    )


def print_per_class_accuracy(class_names, y_true, y_pred):
    print("\nPer-class accuracy:")
    for idx, class_name in enumerate(class_names):
        mask = y_true == idx
        total = int(mask.sum())
        if total == 0:
            print(f"  {class_name:15s} no validation images")
            continue
        correct = int((y_pred[mask] == idx).sum())
        acc = correct / total
        print(f"  {class_name:15s} {acc:6.2%} ({correct}/{total})")


def parse_args():
    base_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Evaluate saved ingredient CNN accuracy.")
    parser.add_argument("--dataset-dir", default=str(base_dir / "dataset_augmented"))
    parser.add_argument("--model-path", default=str(base_dir / "ingredient_model.keras"))
    parser.add_argument("--class-names", default=str(base_dir / "class_names.json"))
    parser.add_argument("--validation-split", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--img-size", type=int, default=224)
    parser.add_argument("--batch-size", type=int, default=32)
    return parser.parse_args()


def main():
    args = parse_args()
    dataset_dir = Path(args.dataset_dir)
    model_path = Path(args.model_path)
    class_names_path = Path(args.class_names)

    if not dataset_dir.is_dir():
        raise FileNotFoundError(f"Dataset folder not found: {dataset_dir}")
    if not model_path.is_file():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    class_names = load_class_names(class_names_path)
    dataset_folders = sorted(p.name for p in dataset_dir.iterdir() if p.is_dir())
    ignored = [name for name in dataset_folders if name not in class_names]

    image_paths, y_true, counts = collect_images(
        dataset_dir=dataset_dir,
        class_names=class_names,
        validation_split=args.validation_split,
        seed=args.seed,
    )
    if not image_paths:
        raise ValueError("No validation images found for the saved class names.")

    print(f"Model: {model_path}")
    print(f"Dataset: {dataset_dir}")
    print(f"Classes from class_names.json: {len(class_names)}")
    print(f"Validation images: {len(image_paths)}")
    if ignored:
        print(f"Ignored folders not in saved class list: {', '.join(ignored)}")

    missing = [name for name, count in counts.items() if count == 0]
    if missing:
        print(f"Missing class folders/images: {', '.join(missing)}")

    model = tf.keras.models.load_model(model_path, compile=False)
    output_classes = int(model.output_shape[-1])
    if output_classes != len(class_names):
        raise ValueError(
            f"Model outputs {output_classes} classes, but class_names.json has "
            f"{len(class_names)} classes."
        )

    ds = make_dataset(image_paths, y_true, args.img_size, args.batch_size)
    probabilities = model.predict(ds, verbose=1)
    y_pred = np.argmax(probabilities, axis=1)

    correct = int((y_pred == y_true).sum())
    total = int(len(y_true))
    print("\nOverall accuracy:")
    print(f"  {correct}/{total} = {correct / total:.2%}")
    print_per_class_accuracy(class_names, y_true, y_pred)


if __name__ == "__main__":
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
    main()

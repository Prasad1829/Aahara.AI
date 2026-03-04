import argparse
import json
import os

import tensorflow as tf


def build_model(num_classes: int) -> tf.keras.Model:
    base = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights="imagenet",
    )
    base.trainable = False  # Freeze base first

    model = tf.keras.Sequential(
        [
            tf.keras.layers.Rescaling(1.0 / 255),
            base,
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(256, activation="relu"),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(num_classes, activation="softmax"),
        ]
    )
    return model, base


def parse_args():
    parser = argparse.ArgumentParser(description="Train ingredient classifier from dataset folders.")
    parser.add_argument(
        "--dataset-dir",
        default="P:/INFOSYS PROJECT/phase4_cnn_model/dataset_augmented",
        help="Path to dataset root where each class has its own folder.",
    )
    parser.add_argument("--epochs", type=int, default=30)         # Increased from 12 to 30
    parser.add_argument("--fine-tune-epochs", type=int, default=10) # Extra fine-tune epochs
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--img-size", type=int, default=224)
    parser.add_argument("--val-split", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main():
    args = parse_args()

    if not os.path.isdir(args.dataset_dir):
        raise FileNotFoundError(f"Dataset folder not found: {args.dataset_dir}")

    print(f"\n📁 Dataset: {args.dataset_dir}")

    train_ds = tf.keras.utils.image_dataset_from_directory(
        args.dataset_dir,
        validation_split=args.val_split,
        subset="training",
        seed=args.seed,
        image_size=(args.img_size, args.img_size),
        batch_size=args.batch_size,
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        args.dataset_dir,
        validation_split=args.val_split,
        subset="validation",
        seed=args.seed,
        image_size=(args.img_size, args.img_size),
        batch_size=args.batch_size,
    )

    class_names = train_ds.class_names
    num_classes = len(class_names)
    print(f"✅ Found {num_classes} classes: {class_names}")

    if num_classes < 2:
        raise ValueError("Need at least 2 classes to train a classifier.")

    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(buffer_size=autotune)
    val_ds = val_ds.prefetch(buffer_size=autotune)

    # ─────────────────────────────────────────────
    # PHASE 1 — Train with frozen base
    # ─────────────────────────────────────────────
    print("\n🔵 PHASE 1: Training with frozen MobileNetV2 base...")
    model, base = build_model(num_classes)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=5,                    # Increased patience
            restore_best_weights=True,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
        ),
    ]

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        callbacks=callbacks,
        verbose=1,
    )

    # ─────────────────────────────────────────────
    # PHASE 2 — Fine-tune: Unfreeze top layers of base
    # ─────────────────────────────────────────────
    print("\n🟠 PHASE 2: Fine-tuning top layers of MobileNetV2...")
    base.trainable = True

    # Freeze all layers except last 30
    for layer in base.layers[:-30]:
        layer.trainable = False

    # Recompile with lower learning rate for fine-tuning
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    fine_tune_callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=5,
            restore_best_weights=True,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
        ),
    ]

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.fine_tune_epochs,
        callbacks=fine_tune_callbacks,
        verbose=1,
    )

    # ─────────────────────────────────────────────
    # SAVE MODEL
    # ─────────────────────────────────────────────
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "ingredient_model.keras")
    class_names_path = os.path.join(base_dir, "class_names.json")

    model.save(model_path)
    with open(class_names_path, "w", encoding="utf-8") as f:
        json.dump(class_names, f, indent=2)

    print("\n" + "=" * 50)
    print("✅ Training Complete!")
    print(f"💾 Saved model      : {model_path}")
    print(f"💾 Saved class names: {class_names_path}")
    print(f"🥦 Classes          : {class_names}")
    print("=" * 50)
    print("\n▶️  NEXT STEP: Restart your backend and test with vegetable images!")


if __name__ == "__main__":
    main()

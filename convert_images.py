import os
from PIL import Image

dataset_path = "dataset_images"

for root, dirs, files in os.walk(dataset_path):
    for file in files:
        file_path = os.path.join(root, file)

        try:
            img = Image.open(file_path).convert("RGB")
            img.save(file_path, "JPEG")
        except Exception as e:
            print("Problem with:", file_path)

print("✅ All images converted to proper JPEG format.")

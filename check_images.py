import os
from PIL import Image

dataset_path = "dataset_images"

for root, dirs, files in os.walk(dataset_path):
    for file in files:
        file_path = os.path.join(root, file)
        try:
            img = Image.open(file_path)
            img.verify()  # check if image is valid
        except Exception as e:
            print("Deleting corrupted file:", file_path)
            os.remove(file_path)

print("✅ Image check completed.")

import cv2
import os

# --- Step 1: Set your project folder ---
project_folder = r"C:\Users\fazik\ingredient_project"

# --- Step 2: Find a .jpg image in the folder ---
image_file = None
for file in os.listdir(project_folder):
    if file.lower().endswith(".jpg") or file.lower().endswith(".jpeg"):
        image_file = file
        break

if image_file is None:
    print("Error: No .jpg image found in the folder.")
    exit()

image_path = os.path.join(project_folder, image_file)
print(f"Using image: {image_path}")

# --- Step 3: Load the image ---
image = cv2.imread(image_path)
if image is None:
    print("Error: Cannot load the image. Check the file.")
    exit()

# --- Step 4: Example detected ingredients ---
# Replace this with your actual detection results
detected_ingredients = [
    {"name": "Tomato", "bbox": [50, 30, 200, 180]},
    {"name": "Onion", "bbox": [220, 50, 350, 200]}
]

# --- Step 5: Draw bounding boxes and labels ---
for ingredient in detected_ingredients:
    x1, y1, x2, y2 = ingredient["bbox"]
    name = ingredient["name"]

    # Draw rectangle
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Put label above the rectangle
    cv2.putText(image, name, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX,
                0.9, (0, 255, 0), 2)

# --- Step 6: Display the image ---
cv2.imshow("Detected Ingredients", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# --- Step 7: Print ingredients ---
print("Detected Ingredients:")
for ingredient in detected_ingredients:
    print(f"- {ingredient['name']}")

# --- Step 8: Save output image ---
output_path = os.path.join(project_folder, "output_detected.jpg")
cv2.imwrite(output_path, image)
print(f"Output saved to: {output_path}")

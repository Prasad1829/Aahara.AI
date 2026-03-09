import cv2
from PIL import Image

# Image path
image_path = "images/image_test.jpg"

# 1️⃣ Read image using OpenCV
image = cv2.imread(image_path)

if image is None:
    print("Image not found! Check file path.")
else:
    print("Image loaded successfully!")

# 2️⃣ Display original image
cv2.imshow("Original Image", image)

# 3️⃣ Convert to Grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
cv2.imshow("Grayscale Image", gray)

# 4️⃣ Save grayscale image
cv2.imwrite("images/image_gray.jpg", gray)

# 5️⃣ Convert JPG → PNG using PIL
img = Image.open(image_path)
img.save("images/image_converted.png")

print("Image converted and saved successfully!")

cv2.waitKey(0)
cv2.destroyAllWindows()

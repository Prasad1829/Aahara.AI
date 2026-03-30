import cv2
import pytesseract
img = cv2.imread("phase1 installation,testing/photo2.jpg")
if img is None:
    print("OCR test image not found.")
    exit()
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
text = pytesseract.image_to_string(gray)
print("Extracted Text:\n", text)

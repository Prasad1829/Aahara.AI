import cv2
import pytesseract

img = cv2.imread(r"P:\INFOSYS PROJECT\phase5_OCR\input\coffe.jpg")

if img is None:
    print("ERROR: Image not found. Check path.")
    exit()

img_show = cv2.resize(img, (900, 600))

# ROI selection (drag and select)
roi_box = cv2.selectROI("Select ROI", img_show, showCrosshair=True)
cv2.destroyAllWindows()

x, y, w, h = roi_box
if w == 0 or h == 0:
    print("ROI not selected!")
    exit()

roi = img_show[y:y+h, x:x+w]

# Upscale + Sharpen + Adaptive Threshold
gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

sharp = cv2.addWeighted(gray, 1.5, cv2.GaussianBlur(gray, (0, 0), 3), -0.5, 0)

thresh = cv2.adaptiveThreshold(
    sharp, 255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY, 31, 10
)

# OCR
config = r'--oem 3 --psm 6'
text = pytesseract.image_to_string(thresh, config=config)

print("----- OCR OUTPUT -----")
print(text)

# Show only preprocessing result (debug)
cv2.imshow("Sharpen", sharp)
cv2.imshow("Adaptive Threshold", thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()


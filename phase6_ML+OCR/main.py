import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import tensorflow as tf
tf.get_logger().setLevel("ERROR")
import cv2
import re
from ocr_module import extract_text_with_ocr
from ml_module import predict_ingredient
# Change image here
image_path = "phase6_ML+OCR/input/test2vegetable.jpg"
img = cv2.imread(image_path)
if img is None:
    print("Image not found!")
    exit()
text = extract_text_with_ocr(image_path)
final_list = []
# ---------------- PACKAGED DETECTION ----------------
packaged_keywords = [
    "ingredients", "nutrition", "net wt", "manufactured",
    "mrp", "best before", "expiry", "contains"
]
is_packaged = False
for kw in packaged_keywords:
    if kw.lower() in text.lower():
        is_packaged = True
        break
# ---------------- PACKAGED ----------------
if is_packaged:
    print("PACKAGED ITEM DETECTED")

    ingredient_line = None
    for line in text.split("\n"):
        if "ingredients" in line.lower():
            ingredient_line = line.strip()
            break

    if ingredient_line is None:
        ingredient_line = "Ingredients not found"

    ingredient_line = re.sub(r"[^a-zA-Z0-9(),:% ]", "", ingredient_line)

    final_list = [ingredient_line]
    print("FINAL OUTPUT LIST =", final_list)

    # Text on image (BLACK)
    cv2.putText(img, "PACKAGED (OCR)", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)

    cv2.putText(img, ingredient_line[:60], (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

# ---------------- RAW ----------------
else:
    print("RAW INGREDIENT DETECTED")

    pred, conf = predict_ingredient(image_path)

    # Confidence threshold
    if conf < 0.60:
        pred = "Unknown"

    final_list = [pred]

    print("FINAL OUTPUT LIST =", final_list)
    print("CONFIDENCE =", round(conf * 100, 2), "%")

    label = f"{pred} ({round(conf*100,2)}%)"

    # Text on image (BLACK)
    cv2.putText(img, "RAW (ML)", (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0),2)

    cv2.putText(img, label, (20, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0),2)

# Show final image
img_show = cv2.resize(img, (900, 600))
cv2.imshow("FINAL RESULT", img_show)
cv2.waitKey(0)
cv2.destroyAllWindows()

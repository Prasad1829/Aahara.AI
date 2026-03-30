import cv2
img = cv2.imread("phase1 installation,testing/photo2.jpg")
if img is None:
    print("image not found")
else:
    print("Image loaded successfully:", img.shape)
    cv2.imshow("Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
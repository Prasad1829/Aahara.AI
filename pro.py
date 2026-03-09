import pytesseract
from PIL import Image

# optional (safety ke liye path manually bhi de dete hain)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

print(pytesseract.get_tesseract_version())

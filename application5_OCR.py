# -*- coding: utf-8 -*-

import pytesseract
from PIL import Image

def main():
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    img = Image.open(r"C:\Users\simon\Desktop\image-800 (1).jpg")
    #img.show()
    print(pytesseract.image_to_string(img, lang="Japanese"))


if __name__ == "__main__":
    main()
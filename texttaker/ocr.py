import pdf2image
import pytesseract
from PIL import Image
from typing import List, Any, Callable

# Convert PDF to image
def convert_pdf_to_image(pdf_path: str) -> List[Image.Image]:
    '''
    Convert pdf to image

    Args:
        pdf_path (str): Path to pdf file
    
    Returns:
        List[Image.Image]: List of images extracted from pdf
    '''
    return pdf2image.convert_from_path(pdf_path, dpi=200)

# Convert image to text
def convert_image_to_text(image: Image.Image, operSyst: str, tesseract_cmd: str = None) -> str:
    '''
    Convert image to text

    Args:
        image (Image.Image): Image to be converted to text
        operSyst (str): Operating system where the script is running
        tesseract_cmd (str): Path to tesseract.exe file (only for Windows)
    
    Returns:
        str: Text extracted from image
    '''
    if operSyst == 'windows':
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    return pytesseract.image_to_string(image, output_type=pytesseract.Output.STRING)
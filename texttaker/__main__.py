import argparse
import os
import pdf2image
import pytesseract
from PIL import Image
import time
import functools
from typing import List, Any, Callable
import concurrent.futures
import json
from writeWordDoc import writeWordDoc
import warnings

def timer(func : Callable) -> Callable:
    '''
    Timer function to be used as a decorator
    
    Args:
        func (Callable): Function to be timed
        
    Returns:
        Callable: Function with timer
        
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        func.__globals__['compute_time'] = float(f"{(end - start):.2f}")
        print(f"\n\tTime taken for {func.__name__} is {(end - start):.2f} seconds \n")
        return result
    return wrapper

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
def convert_image_to_text(image: Image.Image, operSyst: str):
    '''
    Convert image to text

    Args:
        image (Image.Image): Image to be converted to text
        operSyst (str): Operating system where the script is running
    
    Returns:
        str: Text extracted from image
    '''
    if operSyst == 'windows':
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    return pytesseract.image_to_string(image, output_type=pytesseract.Output.STRING)

def check_is_pdf(file: str) -> bool:
    '''
    Check if file is pdf
    
    Args:
        file (str): File path
        
    Returns:
        bool: True if file is pdf, False otherwise
    
    '''
    return file.endswith('.pdf')

def check_is_dir(dirpath: str) -> bool:
    '''
    Check if dirpath is a directory

    Args:
        dirpath (str): Directory path

    Returns:
        bool: True if dirpath is a directory, False otherwise

    '''
    return os.path.isdir(dirpath)

def check_path(path: str):
    """
    check_path: checks if path is valid.

    Args:
        path (string): source folder path.

    Raises an exception if the source folder path is not valid.
    """
    if not os.path.exists(path):
        raise Exception('#ERROR#: {} NOT EXISTS!'.format(path))
    return True

@timer
def get_text_from_pdf(pdf_path: str, max_workers: int, operSyst: str) -> List[str]:
    '''
    Extract text from pdf using more than one process to reduce time processing
    
    Args:
        pdf_path (str): Path to pdf file
        max_workers (int): Number of process to be running at the same time
        operSyst (str): Operating system where the script is running
        
    Returns:
        List[str]: List of text extracted from pdf
    
    '''
    images = convert_pdf_to_image(pdf_path)
    text = ""
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as process_pool:
        for result in process_pool.map(functools.partial(convert_image_to_text, operSyst=operSyst), images):
            text += result

    print(text)       
    return(text)
@timer
def extractText(path: str, max_workers: int, operSyst: str,  msdoc: bool, msdocpath: str): 
    '''
    Extract text from pdf using more than one process to reduce time processing. Write the result in a json file and in a word document if the user wants it.

    Args:
        path (str): Path to pdf file
        max_workers (int): Number of process to be running at the same time
        operSyst (str): Operating system where the script is running
        msdoc (bool): True if user wants to write the result in a word document, False otherwise
        msdocpath (str): Path to save the word document

    '''
    counter = 0
    text = dict()
    data = dict()
    if check_path(path):
        if check_is_dir(path):
            for item in os.listdir(path):
                if check_is_pdf(item):
                    counter += 1
                    print("Processing file: ", counter)
                    text['text'] = get_text_from_pdf(os.path.join(path, item), max_workers, operSyst)
                    text['compute_time(s)'] = compute_time
                    data[item] = text
                if not check_is_pdf(item):
                    print("File {} is not a pdf file".format(item))
                if check_is_dir(item):
                    extractText(os.path.join(path, item), max_workers)
            dir_path = path
        if check_is_pdf(path):
            print("Processing file: ", counter)
            text['text'] = get_text_from_pdf(os.path.join(path, item), max_workers, operSyst)
            text['compute_time(s)'] = compute_time
            data[os.path.basename(path)] = text
            dir_path = os.path.dirname(path)
        if (not check_is_pdf(path)) and counter == 0:
            print("File {} is not a pdf file".format(path))
    print(json.dumps(data, indent=4, sort_keys=True))
    path_to_save_json = "./"+ dir_path + "/text_extracted.json"
    with open(path_to_save_json, "w", encoding='utf8') as f:
      f.write(json.dumps(data, indent=4, ensure_ascii=False))
    if msdoc:
        writeWordDoc(path_to_save_json, msdocpath)
    

def main():
    parser = argparse.ArgumentParser(prog='texttaker', description='Extract text from PDF using more than one process to reduce time processing', epilog='If you need help, please contact ivan.rafa.16@gmail.com')
    parser.add_argument('-p', '--path', help='Path to pdf file or dir containing pdfs files', type=str, required=True)
    parser.add_argument('-w', '--workers', help='Number of processes to be running at the same time (default: %(default)s)', type=int, default=4, choices=range(1, 17))
    parser.add_argument('-operSyst', '--operSyst', help='Operating system (default: %(default)s)', type=str, default='windows', choices=['windows', 'linux'])
    parser.add_argument('-msdoc', '--msdoc', help='Microsoft Word document (default: %(default)s)', action="store_true")
    parser.add_argument('-msdocpath', '--msdocpath', help='Path to the folder to save Microsoft Office Word documents (default: %(default)s)', type=str, default='./data/word_docs')
    args = parser.parse_args()
    if args.msdoc == False and args.msdocpath != './data/word_docs':
        parser.error("argument -msdoc is required if -msdocpath is used")
    if args.msdoc == True and args.msdocpath == './data/word_docs':
        warnings.warn("\t #The words documents will be saved in the default path: ./data/word_docs#")
    extractText(args.path, args.workers, args.operSyst, args.msdoc, args.msdocpath)

if __name__ == "__main__":
    # extractText(path='./data', max_workers=16)
    # python texttaker -p ./data -w 16
    # python texttaker -p ./data -w 16 -msdoc -msdocpath ./data/word_docs 
    extractText(path='./data', max_workers=16, operSyst='windows', msdoc=True, msdocpath='./data/word_docs')
    # main()

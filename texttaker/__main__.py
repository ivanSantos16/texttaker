import argparse
import os
import time
import functools
from typing import List, Any, Callable
import concurrent.futures
import json
from verifiers import check_is_pdf, check_is_dir, check_path
from ocr import convert_image_to_text, convert_pdf_to_image
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

@timer
def get_text_from_pdf(pdf_path: str, max_workers: int, operSyst: str, tesseract_cmd: str = None) -> List[str]:
    '''
    Extract text from pdf using more than one process to reduce time processing
    
    Args:
        pdf_path (str): Path to pdf file
        max_workers (int): Number of process to be running at the same time
        operSyst (str): Operating system where the script is running
        tesseract_cmd (str, optional): Path to tesseract.exe. Defaults to None.
        
    Returns:
        List[str]: List of text extracted from pdf
    
    '''
    images = convert_pdf_to_image(pdf_path)
    text = ""
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as process_pool:
        for result in process_pool.map(functools.partial(convert_image_to_text, operSyst=operSyst, tesseract_cmd=tesseract_cmd), images):
            text += result

    print(text)       
    return(text)
@timer
def extractText(path: str, max_workers: int, operSyst: str,  msdoc: bool, msdocpath: str, tesseract_cmd: str = None, iteration: int = None, counter: int = None, root: str = None, data: dict = None): 
    '''
    Extract text from pdf using more than one process to reduce time processing. Write the result in a json file and in a word document if the user wants it.

    Args:
        path (str): Path to pdf file
        max_workers (int): Number of process to be running at the same time
        operSyst (str): Operating system where the script is running
        msdoc (bool): True if user wants to write the result in a word document, False otherwise
        msdocpath (str): Path to save the word document
        tesseract_cmd (str, optional): Path to tesseract.exe. Defaults to None.
        iteration (int, optional): Number of iteration. Defaults to None. Variable used to control the number of iteration in the recursive function. On first iteration, delete json file if it exists.
        counter (int, optional): Number of files processed. Defaults to None. Variable used to control the number of files inside the data collected from files.
        root (str, optional): Root path. Defaults to None. Variable used to define the root path to save the json file after recursion.

    '''
    if root == None:
        root = path
    if iteration == None:
        iteration = 1
    if counter == None:
        counter = 0
    if data == None:
        data = dict()
    path_to_save_json = root + "/text_extracted.json"
    if iteration == 1 and os.path.exists(path_to_save_json):
        os.remove(path_to_save_json)
    if check_path(path):
        if check_is_dir(path):
            for item in os.listdir(path):
                if check_is_pdf(item):
                    counter = len(data) + 1
                    print("Processing file: ", counter, " | File Name: ", item)
                    # text['text'] = get_text_from_pdf(os.path.join(path, item), max_workers, operSyst)
                    # text['compute_time(s)'] = compute_time
                    data[item] = dict()
                    data[item]['text'] = get_text_from_pdf(os.path.join(path, item), max_workers, operSyst, tesseract_cmd=tesseract_cmd)
                    data[item]['compute_time(s)'] = compute_time
                if check_is_dir(os.path.join(path, item)):
                    extractText(path=os.path.join(path, item), max_workers=max_workers, operSyst=operSyst, msdoc=msdoc, msdocpath=msdocpath, tesseract_cmd=tesseract_cmd, iteration=iteration+1, counter=counter, root = root, data = data)
                if not check_is_pdf(item):
                    print("File {} is not a pdf file".format(item))
            dir_path = path
        if check_is_pdf(path):
            counter += 1
            print("Processing file: ", counter)
            data[os.path.basename(path)] = dict()
            data[os.path.basename(path)]['text'] = get_text_from_pdf(path, max_workers, operSyst, tesseract_cmd)
            data[os.path.basename(path)]["compute_time(s)"] = compute_time
            root = './' + os.path.dirname(path)
        if (not check_is_pdf(path)) and counter == 0:
            print("File {} is not a pdf file".format(path))
    print(json.dumps(data, indent=4, sort_keys=True))
    if os.path.exists(path_to_save_json):
        with open(path_to_save_json, 'r',  encoding='utf8') as f:
            data_from_file = json.load(f)
            data.update(data_from_file)
    with open(path_to_save_json, "w", encoding='utf8') as f:
      f.write(json.dumps(data, indent=4, ensure_ascii=False))
    if msdoc:
        writeWordDoc(path_to_save_json, msdocpath)
    

def main():
    parser = argparse.ArgumentParser(prog='texttaker', description='Extract text from PDF using more than one process to reduce time processing', epilog='If you need help, please contact ivan.rafa.16@gmail.com')
    parser.add_argument('-p', '--path', help='Path to pdf file or dir containing pdfs files', type=str, required=True)
    parser.add_argument('-w', '--workers', help='Number of processes to be running at the same time (default: %(default)s)', type=int, default=4, choices=range(1, 17))
    parser.add_argument('-operSyst', '--operSyst', help='Operating system (default: %(default)s)', type=str, default='linux', choices=['windows', 'linux'])
    parser.add_argument('-tesseractPath', '--tesseractPath', help='Path to tesseract.exe')
    parser.add_argument('-msdoc', '--msdoc', help='Microsoft Word document (default: %(default)s)', action="store_true")
    parser.add_argument('-msdocpath', '--msdocpath', help='Path to the folder to save Microsoft Office Word documents (default: %(default)s)', type=str, default='./data/word_docs')
    args = parser.parse_args()
    if args.msdoc == False and args.msdocpath != './data/word_docs':
        parser.error("argument -msdoc is required if -msdocpath is used")
    if args.msdoc == True and args.msdocpath == './data/word_docs':
        warnings.warn("\t #The words documents will be saved in the default path: ./data/word_docs#")
    if args.operSyst == 'windows' and args.tesseractPath == None:
        parser.error("argument -tesseractPath is required if -operSyst is windows")
    print(args)
    extractText(args.path, args.workers, args.operSyst, args.msdoc, args.msdocpath, tesseract_cmd=args.tesseractPath)

if __name__ == "__main__":
    # extractText(path='./data', max_workers=16)
    # python texttaker -p ./data -w 16 -operSyst windows -tesseractPath C:\Program Files\Tesseract-OCR\tesseract.exe
    # python texttaker -p ./data -w 16 -msdoc -msdocpath ./data/word_docs 
    # extractText(path='./data', max_workers=16, operSyst='windows', msdoc=True, msdocpath='./data/word_docs', tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    main()

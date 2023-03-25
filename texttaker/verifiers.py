import os

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
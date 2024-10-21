import os

KEY_WORD_DATA_FOLDER = 'output.out'

def scan_folders(root_dir : str) -> list:
    """
    Scans through the directory tree starting from root_dir and collects the 
    paths of all folders within the directory structure.
    
    Returns a list of folder paths.
    """

    folder_paths = []
    for root, dirs, _ in os.walk(root_dir):
        for folder in dirs:
            folder_paths.append(os.path.join(root, folder))
    return folder_paths

def is_correct_folder(folder : str, verbose : bool = False) -> bool:
    """
    Checks if the given folder contains a file whose name matches 
    KEY_WORD_DATA_FOLDER.
    
    Returns True if such a file exists, otherwise returns False.
    """
    full_path = ''
    for item in os.listdir(folder):
        full_path = os.path.join(folder, item)
        if os.path.isfile(full_path) and (os.path.basename(full_path) == KEY_WORD_DATA_FOLDER):
            if verbose:
                print(f"The folder {full_path} is valid")
            return True
    if verbose:
        print(f"The folder {full_path} is not valid")
    return False

def scan(data_directory : str) -> list:
    folders = list()
    for folder in scan_folders(data_directory):
        if is_correct_folder(folder):
            folders.append(folder)
    return folders

if __name__ == '__main__':
    # Step 1.1
    data_directory = r'E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_in'
    scan(data_directory)
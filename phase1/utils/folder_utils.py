import os
import warnings
import shutil
from utils_com.logger import ServerLogger

def create_folder(path: str, verbose: bool = False) -> None:

    # Check if the directory exists
    if not os.path.exists(path):
        # Create the directory if it doesn't exist
        os.makedirs(path)
        if verbose: 
            print(f"Directory '{path}' created successfully.")
    else:
        # Raise a warning if the directory already exists
        if verbose: 
            warnings.warn(f"Directory '{path}' already exists.")

def delete_folder(path: str, verbose: bool = False) -> None:
    # Check if the folder exists
    if os.path.exists(path):
        # Delete the folder
        shutil.rmtree(path)
        if verbose: 
            print(f"Folder '{path}' deleted.")
    else:
        if verbose: 
            warnings.warn(f"Folder '{path}' does not exist.")

def copy_one_file(source : str, destination : str, verbose: bool =  False) -> None:
    # Copy the file and capture the returned destination path
    # Check if the returned path matches the expected destination path
    if shutil.copy(source, destination) == destination:
        if verbose: 
            print(f"File copied successfully! {source} -> {destination}")
    else:
        if verbose: 
            print("File copy failed.")

def delete_file(path : str, verbose: bool = False) -> None:
    # Check if the file exists
    LOGGER = ServerLogger()

    if os.path.exists(path):
        try:
            # Remove the file
            os.remove(path)
            if verbose:
                print(f"File '{path}' has been deleted successfully.")
        except Exception as e:
            LOGGER.log(f"Error occurred while deleting the file: {e}")
    else:
        if verbose:
            print(f"File '{path}' does not exist.")
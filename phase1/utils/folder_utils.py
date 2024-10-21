import os
import warnings
import shutil

def create_folder(path: str) -> None:

    # Check if the directory exists
    if not os.path.exists(path):
        # Create the directory if it doesn't exist
        os.makedirs(path)
        print(f"Directory '{path}' created successfully.")
    else:
        # Raise a warning if the directory already exists
        warnings.warn(f"Directory '{path}' already exists.")

def delete_folder(path: str) -> None:
    # Check if the folder exists
    if os.path.exists(path):
        # Delete the folder
        shutil.rmtree(path)
        print(f"Folder '{path}' deleted.")
    else:
        warnings.warn(f"Folder '{path}' does not exist.")

def copy_one_file(source : str, destination : str) -> None:
    # Copy the file and capture the returned destination path
    # Check if the returned path matches the expected destination path
    if shutil.copy(source, destination) == destination:
        print(f"File copied successfully! {source} -> {destination}")
    else:
        print("File copy failed.")

def delete_file(path : str) -> None:
    # Check if the file exists
    if os.path.exists(path):
        try:
            # Remove the file
            os.remove(path)
            print(f"File '{path}' has been deleted successfully.")
        except Exception as e:
            print(f"Error occurred while deleting the file: {e}")
    else:
        print(f"File '{path}' does not exist.")
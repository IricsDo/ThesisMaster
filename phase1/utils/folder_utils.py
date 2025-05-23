import os
import warnings
import shutil
from utils_com.logger import ServerLogger


def create_folder(path: str, verbose: bool = False) -> None:

    LOGGER = ServerLogger()

    # Check if the directory exists
    if not os.path.exists(path):
        # Create the directory if it doesn't exist
        os.makedirs(path)
        if verbose:
            LOGGER.log(f"Directory '{path}' created successfully.")
    else:
        # Raise a warning if the directory already exists
        if verbose:
            LOGGER.log(f"Directory '{path}' already exists.")


def delete_folder(path: str, verbose: bool = False) -> None:
    LOGGER = ServerLogger()

    # Check if the folder exists
    if os.path.exists(path):
        # Delete the folder
        shutil.rmtree(path)
        if verbose:
            LOGGER.log(f"Folder '{path}' deleted.")
    else:
        if verbose:
            warnings.warn(f"Folder '{path}' does not exist.")


def copy_one_file(source: str, destination: str, verbose: bool = False) -> None:
    # Copy the file and capture the returned destination path
    # Check if the returned path matches the expected destination path
    LOGGER = ServerLogger()

    if shutil.copy(source, destination) == destination:
        if verbose:
            LOGGER.log(f"File copied successfully! {source} -> {destination}")
    else:
        if verbose:
            LOGGER.log("File copy failed.")


def move_many_to_one(
    source: list[str], destination: str, copy: bool = False, verbose: bool = False
) -> None:
    """
    Moves or copies multiple folders or files into a single destination folder.

    :param source: List of source paths (folders or files) to move or copy.
    :param destination: Destination folder where all sources will be moved or copied.
    :param verbose: If True, prints details of the operation.
    :param copy: If True, copies instead of moving.
    """

    LOGGER = ServerLogger()

    if not os.path.exists(destination):
        os.makedirs(destination)

    # Track existing names to prevent overwriting
    existing_names = set(os.listdir(destination))
    name_counters = {}

    for src in source:
        if not os.path.exists(src):
            if verbose:
                LOGGER.log(f"Source path does not exist: {src}")
            continue

        base_name = os.path.basename(src)
        dest_path = os.path.join(destination, base_name)

        # Handle duplicate names
        if base_name in existing_names:
            if base_name not in name_counters:
                name_counters[base_name] = 1
            while os.path.exists(dest_path):
                name_counters[base_name] += 1
                name, ext = os.path.splitext(base_name)
                new_name = f"{name}_{name_counters[base_name]}{ext}"
                dest_path = os.path.join(destination, new_name)

        existing_names.add(os.path.basename(dest_path))

        try:
            if copy:
                if os.path.isdir(src):
                    shutil.copytree(src, dest_path)
                else:
                    shutil.copy2(src, dest_path)
            else:
                shutil.move(src, dest_path)
        except Exception as e:
            if verbose:
                LOGGER.log(f"Failed to process {src}: {e}")


def delete_file(path: str, verbose: bool = False) -> None:
    # Check if the file exists
    LOGGER = ServerLogger()

    if os.path.exists(path):
        try:
            # Remove the file
            os.remove(path)
            if verbose:
                LOGGER.log(f"File '{path}' has been deleted successfully.")
        except Exception as e:
            LOGGER.log(f"Error occurred while deleting the file: {e}")
    else:
        if verbose:
            LOGGER.log(f"File '{path}' does not exist, no deleted.")
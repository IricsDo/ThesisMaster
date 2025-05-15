import os
from utils_com.logger import ServerLogger

KEY_WORD_DATA_FOLDER = ["output.out", "TIMES"]


def scan_all_folders(root_dir: str) -> list:
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


def find_all_matching_files(folder: str, verbose: bool = False, index: int = 0) -> list:
    """
    Recursively finds all files in the given folder or its subfolders
    whose names match any entry in KEY_WORD_DATA_FOLDER.

    Returns a list of full paths to the matching files.
    """
    if index >= len(KEY_WORD_DATA_FOLDER) or index < 0:
        raise Exception(
            f"The index must be greater than 0 or less than {len(KEY_WORD_DATA_FOLDER)}"
        )

    matches = []  # To store all matching file paths
    LOGGER = ServerLogger()

    for root, _, files in os.walk(folder):
        if verbose:
            LOGGER.log(f"Checking folder: {root}, files: {files}")
        for file in files:
            if file in KEY_WORD_DATA_FOLDER[index]:
                match_path = os.path.join(root, file)
                matches.append(root)
                if verbose:
                    LOGGER.log(f"Found matching file: {match_path}")
    if verbose and not matches:
        LOGGER.log(f"No valid file found in the directory tree starting at {folder}")
    return matches


def scan(data_directory: str, verbose: bool = False) -> list:
    return find_all_matching_files(data_directory, verbose)

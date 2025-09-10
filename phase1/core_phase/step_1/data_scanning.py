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

def _keep_by_ids(path: str, keep_ids: set[str], base_dir: str) -> bool:
    """_summary_

    Args:
        path (str): _description_
        allowed_ids (set[str]): _description_

    Returns:
        bool: _description_
    """
    if not keep_ids:
        return True
    rel = os.path.relpath(path, base_dir)
    if rel == ".":
        return False  # prevent path == base_dir
    first_segment = rel.split(os.sep, 1)[0]
    return first_segment in keep_ids

def find_all_matching_files(
    folder: str,
    verbose: bool = False,
    index: int = 0,
    allowed_ids: list | set | None = None,
) -> list:
    """
    Recursively finds all files in the given folder or its subfolders
    whose names match any entry in KEY_WORD_DATA_FOLDER.

    Returns a list of full paths to the matching files.
    """
    if index >= len(KEY_WORD_DATA_FOLDER) or index < 0:
        raise Exception(
            f"The index must be greater than 0 or less than {len(KEY_WORD_DATA_FOLDER)}"
        )

    matches = set()  # To store all matching file paths
    LOGGER = ServerLogger()
    target_name = KEY_WORD_DATA_FOLDER[index]
    keep_ids = set(map(str, allowed_ids)) if allowed_ids else set()
    
    for root, _, files in os.walk(folder):
        for file in files:
            if file in target_name:
                if _keep_by_ids(root, keep_ids, folder):
                    matches.add(root)
                    if verbose:
                        LOGGER.log(f"Found matching file: {os.path.join(root, file)}")
                elif verbose:
                    top = os.path.relpath(root, folder).split(os.sep, 1)[0]
                    LOGGER.log(f"[SKIP top-level='{top}'] not in {sorted(keep_ids)}")
                        
    if verbose and not matches:
        LOGGER.log(f"No valid file found in the directory tree starting at {folder}")
        
    return sorted(matches)


def scan(
    data_directory: str,
    verbose: bool = False,
    allowed_ids: list | set | None = None,
    index: int = 0,
) -> list:
    return find_all_matching_files(
        data_directory, verbose=verbose, index=index, allowed_ids=allowed_ids
    )
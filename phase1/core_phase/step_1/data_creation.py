import numpy as np
import dpdata
import os

from utils.folder_utils import create_folder, delete_folder
from phase1.core_phase.step_1.data_scanning import scan, KEY_WORD_DATA_FOLDER


def creation_data_from_siesta(
    data_raw_path: str,
    data_npy_path: str,
    data_size: int,
    key_word_output: str,
    verbose: bool = False,
) -> list[str, str]:
    """
    Processes data from Siesta/aimd_output format and splits it into training and validation sets.

    Parameters:
    - data_raw_path: The path to the directory containing the data.
    - data_size: The number of data points to process. If negative, the function returns an empty list.
    - key_word: A keyword to locate the specific data file within the directory.
    - verbose: Optional flag to enable detailed logging of the data processing steps.

    Returns:
    - A list containing the paths of the saved training and validation datasets.
    """

    if data_size < 0:
        return []

    data = dpdata.LabeledSystem(
        os.path.join(data_raw_path, key_word_output), fmt="siesta/aimd_output"
    )

    index_validation = np.random.choice(
        data_size, size=int(data_size * 0.2), replace=False
    )

    index_training = list(set(range(data_size)) - set(index_validation))
    data_training = data.sub_system(index_training)
    data_validation = data.sub_system(index_validation)

    training_path = "_".join(["training_data", os.path.basename(data_raw_path)])
    validation_path = "_".join(["validation_data", os.path.basename(data_raw_path)])

    data_training.to_deepmd_npy(os.path.join(data_npy_path, training_path))
    data_validation.to_deepmd_npy(os.path.join(data_npy_path, validation_path))

    if verbose:
        print(f"# {data_raw_path} -> {training_path} , {validation_path}")
        print("# the data contains %d frames" % len(data))
        print("# the training data contains %d frames" % len(data_training))
        print("# the validation data contains %d frames" % len(data_validation))

    return [training_path, validation_path]


def extract_data_size(path: str, file_name: str) -> int:
    with open(os.path.join(path, file_name), "r") as file:
        for line in file:
            if "siesta_move" in line:
                value = line.split()[1]
                return int(value)


def creation(new_directory: str, folders: list) -> list:
    if not folders:
        return list()

    delete_folder(new_directory)
    create_folder(new_directory)
    train_val_folders = list()
    for folder in folders:
        data_size = extract_data_size(folder, KEY_WORD_DATA_FOLDER[1])
        train_val_folders.append(
            creation_data_from_siesta(
                folder, new_directory, data_size, KEY_WORD_DATA_FOLDER[0], False
            )
        )
    return train_val_folders


if __name__ == "__main__":

    # Step 1.1
    data_directory = r"E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_in"
    folders = scan(data_directory)

    # Step 1.2
    new_directory = r"E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out"
    train_val_folders = creation(new_directory, folders)

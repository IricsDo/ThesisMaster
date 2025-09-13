import numpy as np
import dpdata
import os
import re

from utils.folder_utils import create_folder, delete_folder
from phase1.core_phase.step_1.data_scanning import scan, KEY_WORD_DATA_FOLDER
from utils_com.logger import ServerLogger
from typing import Tuple, List, Any


def max_min_scale_array(arr: np.ndarray) -> np.ndarray:
    # Compute the min and max of the array
    arr_min = arr.min()
    arr_max = arr.max()
    # Avoid division by zero if all values are equal
    if arr_max - arr_min == 0:
        return arr
    return (arr - arr_min) / (arr_max - arr_min)


def scale_dpdata(data_obj: dpdata.LabeledSystem) -> dpdata.LabeledSystem:
    # Assuming the dpdata object has a dictionary attribute 'data'
    for key, value in data_obj.data.items():
        # Only scale if the value is a numeric numpy array
        if isinstance(value, np.ndarray) and np.issubdtype(
            value.dtype, np.number
        ):  # and key == 'energies':
            data_obj.data[key] = max_min_scale_array(value)
            return data_obj
    return data_obj


def creation_data_from_siesta(
    data_raw_path: str,
    data_npy_path: str,
    data_size: int,
    data_keyword: str,
    num_of_hidro: list = [],
    min_len_data: int = 0,
    task_predict: bool = False,
    verbose: bool = False,
) -> dict:
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
        return {"empty": ["", ""]}

    data = dpdata.LabeledSystem(
        os.path.join(data_raw_path, data_keyword), fmt="siesta/aimd_output"
    )
    LOGGER = ServerLogger()

    if task_predict:
        predict_path = "prediction_data_" + os.path.basename(data_raw_path)
        new_path = os.path.join(data_npy_path, predict_path)
        if not os.path.exists(new_path):
            if verbose:
                LOGGER.log(f"The directory {new_path} does not exist, already created")
            os.makedirs(new_path, exist_ok=True)

        # Apply max-min scaling to each numeric field
        # scaled_data = scale_dpdata(data.copy())
        # scaled_data.to("deepmd/npy", new_path)
        data.to("deepmd/npy", new_path)

        if verbose:
            LOGGER.log(f"# {data_raw_path} -> {predict_path}")
            LOGGER.log("# the data contains %d frames" % len(data))
            LOGGER.log("# the predict data contains %d frames" % len(predict_path))

        return {"predict": [new_path, ""]}

    else:

        if not num_of_hidro:
            raise Exception("Unknow option to get number of atom type")
        
        if data_size <= min_len_data:
            LOGGER.log(
                f"The data size {data_size} is less than the minimum required {min_len_data}, by pass {data_raw_path}"
            )
            return {"empty": ["", ""]} 

        data_training = dpdata.LabeledSystem()
        data_validation = dpdata.LabeledSystem()
        
        index_validation = np.random.choice(
            data_size, size=int(data_size * 0.2), replace=False
        )

        index_training = list(set(range(data_size)) - set(index_validation))
        data_training = data.sub_system(index_training)
        data_validation = data.sub_system(index_validation)

        training_path = "_".join(["training_data", os.path.basename(data_raw_path)])
        validation_path = "_".join(["validation_data", os.path.basename(data_raw_path)])

        # Apply scaling on training and validation sets separately
        # scale_dpdata(data_training)
        # scale_dpdata(data_validation)

        data_training.to_deepmd_npy(os.path.join(data_npy_path, training_path))  # type: ignore
        data_validation.to_deepmd_npy(os.path.join(data_npy_path, validation_path))  # type: ignore

        if verbose:
            LOGGER.log(f"# {data_raw_path} -> {training_path} , {validation_path}")
            LOGGER.log("# the data contains %d frames" % len(data))
            LOGGER.log("# the training data contains %d frames" % len(data_training))
            LOGGER.log(
                "# the validation data contains %d frames" % len(data_validation)
            )

        for i in num_of_hidro:
            if i in os.path.basename(data_raw_path):
                return {i: [training_path, validation_path]}

    return {"empty": ["", ""]}


def creation_data(
    predict_directory: str,
    data_npy_path: str,
    data_size: int,
    data_keyword: str,
    num_of_hidro: list,
    min_len_data : int,
    task_predict: bool = False,
    verbose: bool = False,
) -> dict:

    return creation_data_from_siesta(
        predict_directory,
        data_npy_path,
        data_size,
        data_keyword,
        num_of_hidro,
        min_len_data,
        task_predict,
        verbose,
    )


def extract_data_size(path: str, file_name: str) -> int:
    with open(os.path.join(path, file_name), "r") as file:
        for line in file:
            if "siesta_move" in line:
                value = line.split()[1]
                return int(value)
    return 0


def extract_type_map(path: str, file_name) -> list:
    with open(os.path.join(path, file_name), "r") as file:
        content = file.read()

    match = re.search(
        r"%block ChemicalSpeciesLabel\n(.*?)\n%endblock ChemicalSpeciesLabel",
        content,
        re.DOTALL,
    )
    if match:
        block_content = match.group(1)
        # Find all occurrences of the pattern "number atomic_weight symbol"
        matches = re.findall(r"^\s*(\d+)\s+\d+\s+(\w+)", block_content, re.MULTILINE)
        # Sort the matches by the number and extract the symbols
        sorted_symbols = [
            symbol for _, symbol in sorted(matches, key=lambda x: int(x[0]))
        ]
        return sorted_symbols
    else:
        raise Exception("Not found the atomic type mapping")


def creation(
    data_directory: str,
    folders: list,
    num_of_hidro: list,
    min_len_data: int,
    task_predict: bool = False,
    verbose: bool = False,
) -> Tuple[List[Any], Any]:
    if not folders:
        return [], None

    delete_folder(data_directory)
    create_folder(data_directory)
    data_npy_folders = []
    type_map: Any = None

    for folder in folders:
        data_size = extract_data_size(folder, KEY_WORD_DATA_FOLDER[1])
        type_map = extract_type_map(folder, KEY_WORD_DATA_FOLDER[0])
        result = creation_data(
                folder,
                data_directory,
                data_size,
                KEY_WORD_DATA_FOLDER[0],
                num_of_hidro,
                min_len_data,
                task_predict,
                verbose,
            )
        if result and "empty" not in result:
            data_npy_folders.append(result)
    return data_npy_folders, type_map

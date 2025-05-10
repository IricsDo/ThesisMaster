import os

from utils_com.logger import ServerLogger
from utils.exec_command import execute_command


def train(new_directory: str, tesorflow_fw: bool = True, pytorch_fw: bool = False, verbose: bool = False) -> None:
    LOGGER = ServerLogger()
    if tesorflow_fw:
        command = f"dp --tf train input.json"
    elif pytorch_fw:
        command = f"dp --pt train input.json"
    else:
        raise Exception("Backend not vaild!")
    # command = "dir"
    output, error = execute_command(command, new_directory)
    if verbose:
        LOGGER.log(f"Training output: {output}")
        LOGGER.log(f"Training error: {error}")
    if not error and not output:
        raise Exception("Have the error in train command")


if __name__ == "__main__":

    from phase1.core_phase.step_1.data_scanning import scan, KEY_WORD_DATA_FOLDER
    from phase1.core_phase.step_1.data_creation import creation
    from phase1.core_phase.step_1.data_combine import combine
    from phase1.core_phase.step_2.setup_json import setup_training_input
    from utils.folder_utils import (
        create_folder,
        delete_folder,
        copy_one_file,
        delete_file,
    )
    import concurrent.futures

    # Step 1.1
    data_directory = r"E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_in"
    folders = scan(data_directory)

    # Step 1.2
    new_directory = r"E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out"
    train_val_folders = creation(new_directory, folders)

    # Step 1.3
    combine(new_directory, train_val_folders)

    # Step 2
    source_file = r"E:\Work Spaces\Thesis\Code\Thes, isMaster\phase1\config\input.json"
    new_file = r"E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out\input.json"
    type_map_value = ["C", "H"]
    training_systems = [
        r"E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out\training_data"
    ]
    validation_systems = [
        r"E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out\validation_data"
    ]
    disp_file_value = (
        r"E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out\lcurve.out"
    )
    setup_training_input(
        source_file,
        new_file,
        type_map_value,
        training_systems,
        validation_systems,
        disp_file_value,
    )

    # Step 3.1
    train(new_directory)

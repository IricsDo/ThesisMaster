import json
from utils.folder_utils import delete_file, delete_folder
from utils_com.logger import ServerLogger


def recommend_decay_steps(numb_steps : int, mode : str ="normal") -> int:
    LOGGER = ServerLogger()

    if mode == "slow":
        n = 2
    elif mode == "fast":
        n = 5
    elif mode == "normal":
        n = 3
    else:
        LOGGER.log(f"Decay steps for training invaild ! Set default 5000")
        return 5000
    return numb_steps // n

# Function to modify the JSON file
def modify(
    source_file: str,
    new_file: str,
    type_map_value: str,
    training_systems: list[str],
    validation_systems: list[str],
    disp_file_value: str,
    profiling_file: str,
    tensorboard_log_dir: str,
    numb_steps: int,
    verbose: bool = False,
) -> None:

    # Open and load the JSON data
    with open(source_file, "r") as f:
        data = json.load(f)

    # Modify the values
    data["model"]["type_map"] = type_map_value
    data["model"]["learning_rate"]["decay_steps"] = recommend_decay_steps(numb_steps)
    data["training"]["training_data"]["systems"] = training_systems
    data["training"]["validation_data"]["systems"] = validation_systems
    data["training"]["validation_data"]["numb_btch"] = len(validation_systems)
    data["training"]["disp_file"] = disp_file_value
    data["training"]["profiling_file"] = profiling_file
    data["training"]["tensorboard_log_dir"]= tensorboard_log_dir
    data["training"]["numb_steps"] = numb_steps
    data["training"]["disp_freq"] = int(numb_steps / 50)
    data["training"]["save_freq"] = int(numb_steps / 10)
    data["training"]["tensorboard_freq"] = int(numb_steps / 10)

    # Write the updated data back to the JSON file
    with open(new_file, "w") as f:
        json.dump(data, f, indent=4)


def setup_training_input(
    source_file: str,
    new_file: str,
    type_map_value: str,
    training_systems: list[str],
    validation_systems: list[str],
    disp_file_value: str,
    profiling_file: str,
    tensorboard_log_dir: str,
    numb_steps: int,
    verbose: bool = False,
) -> None:

    delete_file(new_file, verbose)
    delete_file(disp_file_value, verbose)
    delete_file(profiling_file, verbose)
    delete_folder(tensorboard_log_dir, verbose)
    modify(
        source_file,
        new_file,
        type_map_value,
        training_systems,
        validation_systems,
        disp_file_value,
        profiling_file,
        tensorboard_log_dir,
        numb_steps,
        verbose,
    )


if __name__ == "__main__":
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

import json
from utils.folder_utils import delete_file, delete_folder
from utils_com.logger import ServerLogger


def recommend_decay_steps(numb_steps: int, mode: str = "normal") -> int:
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
    stat_file: str,
    numb_steps: int,
    tesorflow_fw: bool,
    pytorch_fw: bool,
    verbose: bool = False,
) -> None:

    LOGGER = ServerLogger()

    if tesorflow_fw and pytorch_fw:
        raise Exception("Backend not vaild!")

    # Open and load the JSON data
    with open(source_file, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            error = f"JSON decode error: {e}"
            LOGGER.log(error)
            raise Exception(error)

    # Modify the values
    data["model"]["type_map"] = type_map_value
    data["training"]["training_data"]["systems"] = training_systems
    data["training"]["validation_data"]["systems"] = validation_systems
    data["training"]["validation_data"]["numb_btch"] = len(validation_systems)
    data["training"]["disp_file"] = disp_file_value
    data["training"]["profiling_file"] = profiling_file
    data["training"]["numb_steps"] = numb_steps
    data["training"]["disp_freq"] = int(numb_steps / 50)
    data["training"]["save_freq"] = int(numb_steps / 10)
    if tesorflow_fw:
        data["learning_rate"]["decay_steps"] = recommend_decay_steps(
            numb_steps
        )
        data["training"]["tensorboard_freq"] = int(numb_steps / 10)
        data["training"]["tensorboard_log_dir"] = tensorboard_log_dir

    else:
        data["learning_rate"]["decay_steps"] = recommend_decay_steps(numb_steps)
        data["training"]["stat_file"] = stat_file

    # Write the updated data back to the JSON file
    with open(new_file, "w") as f:
        json.dump(data, f, indent=4)
    if verbose:
        LOGGER.log("Create training parameter file done!")


def setup_training_input(
    source_file: str,
    new_file: str,
    type_map_value: str,
    training_systems: list[str],
    validation_systems: list[str],
    disp_file_value: str,
    profiling_file: str,
    tensorboard_log_dir: str,
    stat_file: str,
    numb_steps: int,
    tesorflow_fw: bool,
    pytorch_fw: bool,
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
        stat_file,
        numb_steps,
        tesorflow_fw,
        pytorch_fw,
        verbose,
    )

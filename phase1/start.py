import sys
import os
from random import randint

sys.path.append(os.getcwd())
import traceback
import argparse
import json

from utils_com.logger import ServerLogger

TOTAL_PROCESS = 0

LOGGER = ServerLogger()

LOGGER.log(f"Import library...")
try:
    from core_phase.step_1.data_scanning import scan
    from core_phase.step_1.data_creation import creation
    from core_phase.step_1.data_combine import combine
    from core_phase.step_2.setup_json import setup_training_input
    from core_phase.step_3.plot_error import plot_loss
    from core_phase.step_3.train_model import train
    from core_phase.step_4.model_compress import compress, freeze
    from core_phase.step_4.test_model import test
    from core_phase.step_4.valid_model import vaild, predict
    from core_phase.step_4.post_process_data import collect_data_to_one
    from utils_com.traceback_func import run_with_traceback
    from config.return_code import ReturnCode
    from utils.file_utils import is_valid_json, load_json

except Exception as e:
    traceback.print_exc()
    LOGGER.log(f"An error occurred: {e}")
    exit(-1)


def update_process_ui(percent: int) -> None:
    global TOTAL_PROCESS
    TOTAL_PROCESS = randint(TOTAL_PROCESS, percent) if percent != 100 else 100
    LOGGER.log(f"<update_process_ui>{TOTAL_PROCESS}</>")


LOGGER.log(f"Import library success")

update_process_ui(5)

TYPE_MAP = str()
FOLDER_COMBINE = list()


def step1(
    data_directory: str,
    new_directory: str,
    predict_directory: str,
    num_of_hidro: list,
    load_phase1_status: bool,
    verbose: bool,
    bypass: bool = False,
) -> None:
    if bypass:
        LOGGER.log(f"Bypass step 1")
        return
    global TYPE_MAP
    global FOLDER_COMBINE

    status_path =  os.path.join("phase1/phase1_status.json") 
    data = load_json(status_path)

    is_data_available = False

    if load_phase1_status and (data["input_folder"] == data_directory and data["output_folder"] == new_directory):
        try:
            FOLDER_COMBINE = data["phase1"]["step_1"]["FOLDER_COMBINE"]
            TYPE_MAP = data["phase1"]["step_1"]["TYPE_MAP"]

            LOGGER.log("Step 1 found data store in status file, load status")
            LOGGER.log(FOLDER_COMBINE)
            LOGGER.log(TYPE_MAP)
            is_data_available = True
        except:
            LOGGER.log("Step 1 *NOT* found data store in status file, run again")
            is_data_available = False

    if not is_data_available:

        data["input_folder"] = data_directory
        data["output_folder"] = new_directory

        folders = scan(data_directory)
        update_process_ui(10)

        train_val_folders, type_map_train = creation(
            new_directory, folders, num_of_hidro, task_predict=False, verbose=verbose
        )
        update_process_ui(20)

        FOLDER_COMBINE = combine(new_directory, train_val_folders)
        data["phase1"]["step_1"]["FOLDER_COMBINE"] = FOLDER_COMBINE

        update_process_ui(25)
        
        TYPE_MAP = type_map_train
        data["phase1"]["step_1"]["TYPE_MAP"] = TYPE_MAP

    if predict_directory and (data["predict_folder"] != predict_directory):
        LOGGER.log("Step 1 found new prediction folder, make data to predict")
        data["predict_folder"] = predict_directory
        folders = scan(predict_directory)
        _, type_map_predict = creation(
            os.path.join(predict_directory, "result"),
            folders,
            [],
            task_predict=True,
            verbose=verbose,
        )

        if TYPE_MAP != type_map_predict:
            raise Exception("The data for training and prediction is different types.")
    
    data["phase1"]["step_1"]["success"] = True

    with open(status_path, "w") as f:
        json.dump(data, f, indent=4)
    update_process_ui(30)


def step2(
    new_directory: str,
    training_json: str,
    epochs: int,
    tesorflow_fw: bool,
    pytorch_fw: bool,
    load_phase1_status: bool,
    verbose: bool,
    bypass: bool = False,
) -> None:
    if bypass:
        LOGGER.log(f"Bypass step 2")
        return

    global TYPE_MAP
    global FOLDER_COMBINE

    status_path =  os.path.join("phase1/phase1_status.json") 
    data = load_json(status_path)

    is_data_available = False
    config_training_file = ""

    if load_phase1_status:
        try:
            new_training_file = data["phase1"]["step_2"]["new_training_file"]
            config_training_file = data["phase1"]["step_2"]["config_training_file"]
            LOGGER.log("Step 2 found data store in status file, load status")
            LOGGER.log(new_training_file)
            LOGGER.log(training_json)
            is_data_available = True
        except:
            LOGGER.log("Step 2 *NOT* found data store in status file, run again")
            is_data_available = False
    
    if not is_data_available or (config_training_file != training_json):
        config_training_file = training_json
        new_training_file = os.path.join(new_directory, "input.json")
        data["phase1"]["step_2"]["new_training_file"] = new_training_file
        data["phase1"]["step_2"]["config_training_file"] = config_training_file

        type_map_value = TYPE_MAP
        training_systems = [
            item for sublist in FOLDER_COMBINE[0].values() for item in sublist
        ]
        validation_systems = [
            item for sublist in FOLDER_COMBINE[1].values() for item in sublist
        ]
        disp_file_value = os.path.join(new_directory, "lcurve.out")
        profiling_file = os.path.join(new_directory, "timeline.json")
        tensorboard_log_dir = os.path.join(new_directory, "log")
        stat_file = os.path.join(new_directory, "dpa2.hdf5")
        numb_steps = epochs
        setup_training_input(
            config_training_file,
            new_training_file,
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
    
    data["phase1"]["step_2"]["success"] = True

    with open(status_path, "w") as f:
        json.dump(data, f, indent=4)
    update_process_ui(40)


def step3(
    new_directory: str,
    tesorflow_fw: bool,
    pytorch_fw: bool,
    load_phase1_status: bool,
    verbose: bool,
    bypass: bool = False,
) -> None:
    if bypass:
        LOGGER.log(f"Bypass step 3")
        return
    
    status_path =  os.path.join("phase1/phase1_status.json") 
    data = load_json(status_path)

    is_data_available = False

    if load_phase1_status:
        try:
            model_path = data["phase1"]["step_3"]["model_path"]
            LOGGER.log("Step 3 found data store in status file, load status")
            LOGGER.log(model_path)
            is_data_available = True
        except:
            LOGGER.log("Step 3 *NOT* found data store in status file, run again")
            is_data_available = False

    if not is_data_available:
        train(new_directory, tesorflow_fw, pytorch_fw, verbose)
        data["phase1"]["step_3"]["model_path"] = os.path.join(new_directory, "graph.pb" if tesorflow_fw else "graph.pth")
        update_process_ui(60)

        plot_loss(new_directory)


    data["phase1"]["step_3"]["success"] = True

    with open(status_path, "w") as f:
        json.dump(data, f, indent=4)
    update_process_ui(65)


def step4(
    new_directory: str,
    predict_directory: str,
    tesorflow_fw: bool,
    pytorch_fw: bool,
    load_phase1_status: bool,
    verbose: bool,
    bypass: bool = False,
) -> None:
    if bypass:
        LOGGER.log(f"Bypass step 4")
        return
    global FOLDER_COMBINE

    status_path =  os.path.join("phase1/phase1_status.json") 
    data = load_json(status_path)

    is_data_available = False

    if load_phase1_status:
        try:
            image_loss = data["phase1"]["step_4"]["image_loss"]
            LOGGER.log("Step 4 found data store in status file, load status")
            LOGGER.log(image_loss)
            is_data_available = True
        except:
            LOGGER.log("Step 4 *NOT* found data store in status file, run again")
            is_data_available = False

    if not is_data_available:
        freeze(new_directory, tesorflow_fw, pytorch_fw, verbose)
        update_process_ui(70)

        compress(new_directory, tesorflow_fw, pytorch_fw, verbose)
        update_process_ui(75)

        validation_systems = [
            item for sublist in FOLDER_COMBINE[1].values() for item in sublist
        ]
        new_path = collect_data_to_one(new_directory, validation_systems)

        test(new_directory, tesorflow_fw, pytorch_fw, verbose)
        update_process_ui(80)

        vaild(new_directory, new_path, "", tesorflow_fw, pytorch_fw, task_predict=False)
        update_process_ui(85)

        data["phase1"]["step_4"]["image_loss"] = os.path.join(new_directory, "output_loss.png")

    if predict_directory:
        predict(
            "",
            os.path.join(predict_directory, "result"),
            new_directory,
            tesorflow_fw,
            pytorch_fw,
            task_predict=True,
        )

    data["phase1"]["step_4"]["success"] = True

    with open(status_path, "w") as f:
        json.dump(data, f, indent=4)
    update_process_ui(90)


def workflow(
    input_folder: str,
    output_folder: str,
    predict_folder: str,
    training_json: str,
    epochs: int,
    num_of_hidro: list,
    only_make_data: bool,
    tesorflow_fw: bool,
    pytorch_fw: bool,
    load_phase1_status: bool,
    verbose: bool,
) -> int:
    
    if load_phase1_status:
        phase1_status = os.path.join("phase1/phase1_status.json") 

        default_data = {
            "input_folder": input_folder,
            "output_folder": output_folder,
            "predict_folder": predict_folder,
            "phase1": {
                "step_1": {
                    "success" : False
                },
                "step_2": {
                    "success" : False
                },
                "step_3": {
                    "success" : False
                },
                "step_4": {
                    "success" : False
                }
            }
        }
        if not os.path.exists(phase1_status) or not is_valid_json(phase1_status):
            # Create or overwrite the file with correct structure
            with open(phase1_status, "w") as f:
                json.dump(default_data, f, indent=4)
            LOGGER.log(f"{phase1_status} created or overwritten with default structure.")
        else:
            LOGGER.log(f"{phase1_status} already exists and contains valid JSON.")


    LOGGER.log("\n***Step 1/4 in phase 1 on running!\n")
    if run_with_traceback(
        step1, input_folder, output_folder, predict_folder, num_of_hidro, load_phase1_status, verbose
    ):
        return ReturnCode.ERROR_CODE_1
    else:
        LOGGER.log("\n***Step 1/4 in phase 1 run successfully!\n")

    if not only_make_data:
        LOGGER.log("\n***Step 2/4 in phase 1 on running!\n")
        if run_with_traceback(
            step2,
            output_folder,
            training_json,
            epochs,
            tesorflow_fw,
            pytorch_fw,
            load_phase1_status,
            verbose,
        ):
            return ReturnCode.ERROR_CODE_2
        else:
            LOGGER.log("\n***Step 2/4 in phase 1 run successfully!\n")

        LOGGER.log("\n***Step 3/4 in phase 1 on running!\n")
        if run_with_traceback(step3, output_folder, tesorflow_fw, pytorch_fw, load_phase1_status, verbose):
            return ReturnCode.ERROR_CODE_3
        else:
            LOGGER.log("\n***Step 3/4 in phase 1 run successfully!\n")

        LOGGER.log("\n***Step 4/4 in phase 1 on running!\n")
        if run_with_traceback(
            step4, output_folder, predict_folder, tesorflow_fw, pytorch_fw, load_phase1_status, verbose
        ):
            return ReturnCode.ERROR_CODE_4
        else:
            LOGGER.log("\n***Step 4/4 in phase 1 run successfully!\n")
    else:
        LOGGER.log("Mode <<Only Make Data>> on, bypass all steps 2,3,4\n")

    LOGGER.log("Phase 1 run successfully!")
    return ReturnCode.SUCCESS


def main():
    # Create an ArgumentParser object with a custom description
    parser = argparse.ArgumentParser(
        description="A script to parse folder paths from terminal with verbose option and help support."
    )

    # Add arguments for input and output folders (required)
    parser.add_argument(
        "-i",
        "--input_folder",
        type=str,
        required=True,
        help="The input folder to process.",
    )
    parser.add_argument(
        "-o",
        "--output_folder",
        type=str,
        required=True,
        help="The output folder where results will be saved.",
    )

    parser.add_argument(
        "-p",
        "--predict_folder",
        type=str,
        required=False,
        default="",
        help="The predict folder to process.",
    )

    parser.add_argument(
        "-e",
        "--epochs",
        type=int,
        default=10000,
        help="The number of epochs to train the model (default: 10000).",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose mode for detailed output.",
    )

    parser.add_argument(
        "-omd",
        "--only_make_data",
        action="store_true",
        help="Enable only make data mode for input data.",
    )

    parser.add_argument(
        "-tf",
        "--tesorflow",
        action="store_true",
        help="Select framework for backend",
    )

    parser.add_argument(
        "-pt",
        "--pytorch",
        action="store_true",
        help="Using pytorch backend",
    )

    parser.add_argument(
        "-lps1",
        "--load_phase1_status",
        action="store_true",
        help="If system already use this data before, don't need to create data again. Use data are available on folder",
    )

    parser.add_argument(
        "-noh",
        "--num_of_hidro",
        metavar="N",
        type=str,
        nargs="*",
        help="List of different atomic systems.",
    )

    parser.add_argument(
        "-trainj",
        "--training_json",
        type=str,
        required=True,
        help="The training file name is used to configure all parameters.",
    )

    # Parse the arguments
    args = parser.parse_args()

    # Verbose mode check
    if args.verbose:
        LOGGER.log("Verbose mode is enabled.")

    # Check if the input folder exists
    if not os.path.isdir(args.input_folder):
        LOGGER.log(f"Error: Input folder '{args.input_folder}' does not exist.")
        return

    if not args.training_json.endswith(".json"):
        LOGGER.log(f"The config file not vaild, try again or check the correct file")
        return

    # Check if the output folder exists, create it if it doesn't
    if not os.path.isdir(args.output_folder):
        LOGGER.log(
            f"Output folder '{args.output_folder}' does not exist. Creating it..."
        )
        os.makedirs(args.output_folder)

    # If verbose, print the folder paths
    if args.verbose:
        LOGGER.log("-" * 30)
        for key, value in vars(args).items():
            LOGGER.log((f"Name argument: {key} - Value: {value}"))
        LOGGER.log("-" * 30)

    state = workflow(
        args.input_folder,
        args.output_folder,
        args.predict_folder,
        args.training_json,
        args.epochs,
        args.num_of_hidro,
        args.only_make_data,
        args.tesorflow,
        args.pytorch,
        args.load_phase1_status,
        args.verbose,
    )
    LOGGER.log(f"State of workflow phase 1: {ReturnCode.get_message(state)}")
    LOGGER.log(f"\nServer shutdown, bye!\n")
    if state == ReturnCode.SUCCESS:
        update_process_ui(100)


if __name__ == "__main__":
    LOGGER.log(f"\nServer starting, hi!\n")
    try:
        main()
    except SystemExit as e:
        LOGGER.log("\n")
        LOGGER.log(f"An error occurred: {e} => Missing input arguments")

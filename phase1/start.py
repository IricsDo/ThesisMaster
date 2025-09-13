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
    from utils.file_utils import load_json
    from _helper import (
            get_all_folders,
            ensure_predict_data,
            auto_detect_backend,
            _ensure_status_skeleton,
            _reset_downstream,
            _get_model_path,
            _get_model_mtime,
        )
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
    min_len_data: int,
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

    # Safer cache check: also validate num_of_hidro & min_len_data
    if load_phase1_status and (data.get("input_folder") == data_directory and data.get("output_folder") == new_directory):
        try:
            cached_params = data["phase1"]["step_1"].get("params", {})
            same_noh = cached_params.get("num_of_hidro") == (num_of_hidro or [])
            same_mld = cached_params.get("min_len_data") == min_len_data

            if data["phase1"]["step_1"]["success"] and same_noh and same_mld:
                FOLDER_COMBINE = data["phase1"]["step_1"]["FOLDER_COMBINE"]
                TYPE_MAP = data["phase1"]["step_1"]["TYPE_MAP"]
                LOGGER.log("Step 1 cache hit: load FOLDER_COMBINE & TYPE_MAP from status")
                is_data_available = True
            else:
                LOGGER.log("Step 1 cache invalidated: num_of_hidro/min_len_data changed or previous not successful")
                is_data_available = False
        except:
            LOGGER.log("Step 1 *NOT* found cache or cache invalid, rebuild")
            is_data_available = False

    if not is_data_available:
        # step1 changes -> invalidate downstream steps 2-4
        _reset_downstream(data, from_step=2)

        data["input_folder"] = data_directory
        data["output_folder"] = new_directory

        folders = scan(data_directory, verbose=verbose, allowed_ids=num_of_hidro)
        update_process_ui(10)

        train_val_folders, type_map_train = creation(
            new_directory, folders, num_of_hidro or [], min_len_data or 0, task_predict=False, verbose=verbose
        )
        update_process_ui(20)

        FOLDER_COMBINE = combine(new_directory, train_val_folders)
        data["phase1"]["step_1"]["FOLDER_COMBINE"] = FOLDER_COMBINE

        update_process_ui(25)
        
        TYPE_MAP = type_map_train
        data["phase1"]["step_1"]["TYPE_MAP"] = TYPE_MAP

        # store params to validate cache later
        data["phase1"]["step_1"]["params"] = {
            "num_of_hidro": num_of_hidro or [],
            "min_len_data": min_len_data or 0,
        }

    # handle prediction data build separately
    if predict_directory and (data.get("predict_folder") != predict_directory):
        LOGGER.log("Step 1 found new prediction folder, make data to predict")
        data["predict_folder"] = predict_directory
        folders = scan(predict_directory)

        _, type_map_predict = creation(
            os.path.join(predict_directory, "result"),
            folders,
            [],
            0,
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
    tensorflow_fw: bool,  # legacy param name kept for compatibility
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
            prev_cfg = data["phase1"]["step_2"].get("config_training_file", "")
            prev_epochs = data["phase1"]["step_2"].get("epochs", None)
            if data["phase1"]["step_1"]["success"] and data["phase1"]["step_2"]["success"] \
               and prev_cfg == training_json and prev_epochs == epochs:
                LOGGER.log("Step 2 cache hit: reuse previous training input")
                is_data_available = True
            else:
                LOGGER.log("Step 2 cache invalidated: step1 not ready or config/epochs changed")
                is_data_available = False
        except:
            LOGGER.log("Step 2 cache invalid or missing, rebuild")
            is_data_available = False
    
    if not is_data_available:
        config_training_file = training_json
        new_training_file = os.path.join(new_directory, "input.json")
        data["phase1"]["step_2"]["new_training_file"] = new_training_file
        data["phase1"]["step_2"]["config_training_file"] = config_training_file
        data["phase1"]["step_2"]["epochs"] = epochs

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
            tensorflow_fw,
            pytorch_fw,
            verbose,
        )

        # step2 (re)built -> invalidate step3-4
        _reset_downstream(data, from_step=3)
    
    data["phase1"]["step_2"]["success"] = True

    with open(status_path, "w") as f:
        json.dump(data, f, indent=4)
    update_process_ui(40)


def step3(
    new_directory: str,
    tensorflow_fw: bool,  # legacy param name kept for compatibility
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
            prev_success = data["phase1"]["step_3"]["success"]
            model_path = data["phase1"]["step_3"].get("model_path", "")
            prev_framework = data["phase1"]["step_3"].get("framework", "")
            curr_framework = "tensorflow" if tensorflow_fw else "pytorch"
            if prev_success and model_path and os.path.isfile(model_path) and prev_framework == curr_framework:
                LOGGER.log("Step 3 cache hit: trained model available and framework unchanged")
                is_data_available = True
            else:
                LOGGER.log("Step 3 cache invalidated: missing model or framework changed or previous not successful")
                is_data_available = False
        except:
            LOGGER.log("Step 3 cache invalid or missing, (re)train")
            is_data_available = False

    if not is_data_available:
        train(new_directory, tensorflow_fw, pytorch_fw, verbose)
        model_path = _get_model_path(new_directory, tensorflow_fw, pytorch_fw)
        data["phase1"]["step_3"]["model_path"] = model_path
        data["phase1"]["step_3"]["framework"] = "tensorflow" if tensorflow_fw else "pytorch"
        data["phase1"]["step_3"]["model_mtime"] = _get_model_mtime(model_path)
        update_process_ui(60)

        plot_loss(new_directory)

    data["phase1"]["step_3"]["success"] = True

    with open(status_path, "w") as f:
        json.dump(data, f, indent=4)
    update_process_ui(65)


def step4(
    new_directory: str,
    predict_directory: str,
    tensorflow_fw: bool,  # legacy param name kept for compatibility
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

    # reuse only if model mtime unchanged
    curr_model_path = _get_model_path(new_directory, tensorflow_fw, pytorch_fw)
    curr_mtime = _get_model_mtime(curr_model_path)

    if load_phase1_status:
        try:
            prev_success = data["phase1"]["step_4"]["success"]
            prev_image_loss = data["phase1"]["step_4"].get("image_loss", "")
            prev_mtime = data["phase1"]["step_4"].get("model_mtime", None)
            if prev_success and prev_image_loss and prev_mtime == curr_mtime:
                LOGGER.log("Step 4 cache hit: validation artifacts up-to-date")
                is_data_available = True
            else:
                LOGGER.log("Step 4 cache invalidated: model changed or previous not successful")
                is_data_available = False
        except:
            LOGGER.log("Step 4 cache invalid or missing, rebuild")
            is_data_available = False

    if not is_data_available:
        freeze(new_directory, tensorflow_fw, pytorch_fw, verbose)
        update_process_ui(70)

        compress(new_directory, tensorflow_fw, pytorch_fw, verbose)
        update_process_ui(75)

        validation_systems = [
            item for sublist in FOLDER_COMBINE[1].values() for item in sublist
        ]
        type_of_data = "validation_data"
        new_path = collect_data_to_one(new_directory, type_of_data, validation_systems)

        test(new_directory, tensorflow_fw, pytorch_fw, verbose)
        update_process_ui(80)

        vaild(new_directory, new_path, "", tensorflow_fw, pytorch_fw, task_predict=False)
        update_process_ui(85)

        data["phase1"]["step_4"]["image_loss"] = os.path.join(new_directory, "output_loss.png")
        data["phase1"]["step_4"]["model_mtime"] = curr_mtime

    if predict_directory:
        predict(
            "",
            os.path.join(predict_directory, "result"),
            new_directory,
            tensorflow_fw,
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
    min_len_data: int,
    only_make_data: bool,
    tensorflow_fw: bool,  # legacy param name kept for compatibility
    pytorch_fw: bool,
    load_phase1_status: bool,
    verbose: bool,
) -> int:
    
    if load_phase1_status:
        # Ensure skeleton with fields needed for robust cache checks
        _ensure_status_skeleton(input_folder, output_folder, predict_folder)

    LOGGER.log("\n***Step 1/4 in phase 1 on running!\n")
    if run_with_traceback(
        step1, input_folder, output_folder, predict_folder, num_of_hidro, min_len_data, load_phase1_status, verbose
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
            tensorflow_fw,
            pytorch_fw,
            load_phase1_status,
            verbose,
        ):
            return ReturnCode.ERROR_CODE_2
        else:
            LOGGER.log("\n***Step 2/4 in phase 1 run successfully!\n")

        LOGGER.log("\n***Step 3/4 in phase 1 on running!\n")
        if run_with_traceback(step3, output_folder, tensorflow_fw, pytorch_fw, load_phase1_status, verbose):
            return ReturnCode.ERROR_CODE_3
        else:
            LOGGER.log("\n***Step 3/4 in phase 1 run successfully!\n")

        LOGGER.log("\n***Step 4/4 in phase 1 on running!\n")
        if run_with_traceback(
            step4, output_folder, predict_folder, tensorflow_fw, pytorch_fw, load_phase1_status, verbose
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

    # NOTE: Make these NOT required so predict-only mode can run without them
    parser.add_argument(
        "-i",
        "--input_folder",
        type=str,
        required=False,
        help="The input folder to process.",
    )
    parser.add_argument(
        "-o",
        "--output_folder",
        type=str,
        required=False,
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

    # Fixed typo; keep the correct flag name
    parser.add_argument(
        "-tf", "--tensorflow",
        dest="tensorflow",
        action="store_true",
        help="Use TensorFlow backend",
    )

    parser.add_argument(
        "-pt",
        "--pytorch",
        action="store_true",
        help="Use PyTorch backend",
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
        "-mld",
        "--min_len_data",
        type=int,
        default=0,
        help="Number of minimum data length.",
    )

    parser.add_argument(
        "-trainj",
        "--training_json",
        type=str,
        required=False,  # NOT required so predict-only can run
        help="The training file name is used to configure all parameters.",
    )

    # NEW: predict-only specific args
    parser.add_argument(
        "-mp", "--model_path",
        type=str, default="",
        help="Path to pre-trained model (file or directory) for predict-only mode.",
    )
    parser.add_argument(
        "-pred_only", "--predict_only",
        action="store_true",
        help="Enable predict-only mode using model_path and predict_folder.",
    )
    parser.add_argument(
        "--skip_prepare_predict_data",
        action="store_true",
        help="Skip preparing <predict_folder>/result and use it as-is.",
    )

    # Parse the arguments
    args = parser.parse_args()

    # Verbose mode check
    if args.verbose:
        LOGGER.log("Verbose mode is enabled.")

    # --- Predict-only mode (runs BEFORE any training validations) ---
    if args.predict_only:
        if not args.model_path or not args.predict_folder:
            LOGGER.log("Error: --model_path and --predict_folder are required in predict-only mode.")
            return

        # Normalize model_dir (accept file or directory)
        model_dir = args.model_path
        if os.path.isfile(model_dir):
            model_dir = os.path.dirname(model_dir)
        if not os.path.isdir(model_dir):
            LOGGER.log(f"Error: model_path '{args.model_path}' is not a valid file or directory.")
            return

        # Auto-detect backend and the exact model file
        try:
            is_tf, is_pt, model_dir, chosen_model_file = auto_detect_backend(
                args.model_path, args.tensorflow, args.pytorch
            )
        except Exception as det_e:
            LOGGER.log(f"Error: {det_e}")
            return

        # Reflect detection back into args so downstream code stays unchanged
        args.tensorflow = is_tf
        args.pytorch = is_pt

        LOGGER.log(f"Backend detected: {'TensorFlow' if is_tf else 'PyTorch'}")
        LOGGER.log(f"Model directory: {model_dir}")
        LOGGER.log(f"Model file used: {chosen_model_file}")

        LOGGER.log("Running in predict-only mode...")
        update_process_ui(90)

        # Optionally prepare prediction data
        if args.skip_prepare_predict_data:
            result_dir = os.path.join(args.predict_folder, "result")
            if not os.path.isdir(result_dir):
                LOGGER.log(f"Error: '--skip_prepare_predict_data' set, but '{result_dir}' does not exist.")
                return
        else:
            result_dir = ensure_predict_data(args.predict_folder, args.verbose, LOGGER)

        # Run prediction (same signature as used in step4)
        try:
            update_process_ui(95)
            predict(
                "",                     # input_path not used in this mode
                result_dir,             # output folder for results
                model_dir,              # model directory (contains graph.pth / graph.pb)
                args.tensorflow,
                args.pytorch,
                task_predict=True,
            )
            update_process_ui(100)
            LOGGER.log(f"Predict-only completed. Outputs saved to: {result_dir}")
        except Exception:
            traceback.print_exc()
            LOGGER.log("Predict-only failed due to an exception.")
            return

        LOGGER.log(f"\nServer shutdown, bye!\n")
        return
    # --- End predict-only ---

    # ===== Training/standard workflow validations (only when not predict-only) =====
    if not args.input_folder or not os.path.isdir(args.input_folder):
        LOGGER.log(f"Error: Input folder '{args.input_folder}' does not exist.")
        return

    if not args.only_make_data:
        if not args.training_json or not args.training_json.endswith(".json"):
            LOGGER.log("The config file not valid, try again or check the correct file")
            return

    if not args.output_folder:
        LOGGER.log(f"Error: Output folder is not specified.")
        return

    # Check/create output folder
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
        args.min_len_data,
        args.only_make_data,
        args.tensorflow,
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

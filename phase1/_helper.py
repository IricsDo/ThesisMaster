import os
import json
from pathlib import Path

from utils.file_utils import is_valid_json

def ensure_predict_data(predict_directory: str, verbose: bool, logger) -> str:
    """
    Prepare prediction data inside <predict_directory>/result.
    If already prepared (non-empty), reuse it.
    Avoid scanning the 'result' directory to prevent re-entrancy.
    Returns the path to the 'result' folder.
    """
    # Import locally to avoid circular imports at module load time
    from core_phase.step_1.data_scanning import scan
    from core_phase.step_1.data_creation import creation

    os.makedirs(predict_directory, exist_ok=True)
    result_dir = os.path.join(predict_directory, "result")

    # Reuse prepared result if exists and non-empty
    if os.path.isdir(result_dir) and os.listdir(result_dir):
        if verbose:
            logger.log(f"'result' already prepared at: {result_dir}")
        return result_dir

    # Scan sources in predict_directory
    folders = scan(predict_directory)

    # Filter out the result folder itself if scanner picks it up
    folders = [f for f in folders if os.path.abspath(f) != os.path.abspath(result_dir)]
     
    # Build prediction-ready data into <predict_directory>/result
    creation(
        result_dir,
        folders,
        [],
        0,
        task_predict=True,
        verbose=verbose,
    )
    
    return result_dir


def auto_detect_backend(model_path: str, tf_flag: bool, pt_flag: bool):
    """
    Auto-detect backend (TensorFlow vs PyTorch) from model_path and/or flags.

    Returns:
        (is_tensorflow: bool, is_pytorch: bool, model_dir: str, chosen_model_file: str)

    Rules:
      - If both flags set: error (ambiguous).
      - If one flag set: validate that a model of that type exists.
      - If none set:
          * If model_path is a file: infer from extension (.pb -> TF, .pth -> PT).
          * If model_path is a directory: look for graph.pb / graph.pth,
            otherwise glob *.pb / *.pth (shallow). If multiple of same type, take latest by mtime.
      - If both kinds found: error.
    Raises:
      Exception on ambiguity or missing model.
    """
    def pick_latest(files):
        return max(files, key=lambda p: os.path.getmtime(p)) if files else None

    # Normalize model_dir / candidate file
    if os.path.isfile(model_path):
        model_dir = os.path.dirname(model_path)
        cand_file = model_path
    elif os.path.isdir(model_path):
        model_dir = model_path
        cand_file = None
    else:
        raise Exception(f"model_path '{model_path}' is neither a file nor a directory.")

    # Flags contradict each other
    if tf_flag and pt_flag:
        raise Exception("Please choose either --pytorch or --tesorflow, not both.")

    # If a file was provided, infer directly from extension (unless a flag overrides)
    if cand_file:
        lower = cand_file.lower()
        if lower.endswith(".pth"):
            if tf_flag:
                raise Exception("Provided model is .pth (PyTorch) but --tesorflow is set.")
            return (False, True, model_dir, cand_file)
        if lower.endswith(".pb"):
            if pt_flag:
                raise Exception("Provided model is .pb (TensorFlow) but --pytorch is set.")
            return (True, False, model_dir, cand_file)
        # Unknown extension: fall back to directory scan (continue below)

    # Directory scan logic
    tf_canon = os.path.join(model_dir, "graph.pb")
    pt_canon = os.path.join(model_dir, "graph.pth")

    tf_files = [tf_canon] if os.path.isfile(tf_canon) else []
    pt_files = [pt_canon] if os.path.isfile(pt_canon) else []

    # Shallow glob if canonical names not found
    if not tf_files:
        tf_files = [
            os.path.join(model_dir, f)
            for f in os.listdir(model_dir)
            if f.lower().endswith(".pb") and os.path.isfile(os.path.join(model_dir, f))
        ]
    if not pt_files:
        pt_files = [
            os.path.join(model_dir, f)
            for f in os.listdir(model_dir)
            if f.lower().endswith(".pth") and os.path.isfile(os.path.join(model_dir, f))
        ]

    # Apply flags if any
    if tf_flag and not pt_flag:
        if not tf_files:
            raise Exception(f"No TensorFlow model (.pb) found in: {model_dir}")
        chosen = pick_latest(tf_files)
        return (True, False, model_dir, chosen)

    if pt_flag and not tf_flag:
        if not pt_files:
            raise Exception(f"No PyTorch model (.pth) found in: {model_dir}")
        chosen = pick_latest(pt_files)
        return (False, True, model_dir, chosen)

    # No flags: infer from availability
    has_tf = len(tf_files) > 0
    has_pt = len(pt_files) > 0

    if has_tf and has_pt:
        raise Exception("Both .pb and .pth models found. Please specify --pytorch or --tesorflow.")

    if has_tf:
        chosen = pick_latest(tf_files)
        return (True, False, model_dir, chosen)

    if has_pt:
        chosen = pick_latest(pt_files)
        return (False, True, model_dir, chosen)

    raise Exception(
        f"No supported model found in: {model_dir} "
        f"(expected graph.pb or graph.pth or any *.pb/*.pth)"
    )

# -------------------- Added: cache skeleton & invalidation helpers --------------------

def _ensure_status_skeleton(input_folder: str, output_folder: str, predict_folder: str) -> None:
    """
    Ensure phase1/phase1_status.json exists with the fields we rely on for cache validation.
    """
    phase1_status = os.path.join("phase1/phase1_status.json")
    default_data = {
        "input_folder": input_folder,
        "output_folder": output_folder,
        "predict_folder": predict_folder,
        "phase1": {
            "step_1": {"success": False, "FOLDER_COMBINE": [], "TYPE_MAP": "", "params": {}},
            "step_2": {"success": False, "new_training_file": "", "config_training_file": "", "epochs": None},
            "step_3": {"success": False, "model_path": "", "framework": "", "model_mtime": None},
            "step_4": {"success": False, "image_loss": "", "model_mtime": None},
        },
    }
    if not os.path.exists(phase1_status) or not is_valid_json(phase1_status):
        os.makedirs(os.path.dirname(phase1_status), exist_ok=True)
        with open(phase1_status, "w") as f:
            json.dump(default_data, f, indent=4)


def _reset_downstream(data: dict, from_step: int) -> None:
    """
    Reset success flags and critical fields for steps >= from_step.
    """
    if from_step <= 2:
        data["phase1"]["step_2"]["success"] = False
        # keep new_training_file/config recorded, they will be overwritten by step2 if needed
    if from_step <= 3:
        data["phase1"]["step_3"]["success"] = False
        data["phase1"]["step_3"]["model_path"] = ""
        data["phase1"]["step_3"]["framework"] = ""
        data["phase1"]["step_3"]["model_mtime"] = None
    if from_step <= 4:
        data["phase1"]["step_4"]["success"] = False
        data["phase1"]["step_4"]["image_loss"] = ""
        data["phase1"]["step_4"]["model_mtime"] = None


def _get_model_path(new_directory: str, tensorflow_fw: bool, pytorch_fw: bool) -> str:
    """
    Compute expected model path in output_folder based on backend flag.
    """
    return os.path.join(new_directory, "graph.pb" if tensorflow_fw else "graph.pth")


def _get_model_mtime(path: str):
    try:
        return os.path.getmtime(path) if os.path.isfile(path) else None
    except Exception:
        return None



def get_all_folders(path):
    return [str(p.resolve()) for p in Path(path).iterdir() if p.is_dir()]
# ------------------------------------------------------------------------------------
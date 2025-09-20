#!/bin/bash
# ==========================================================
# run_script.sh
# Wrapper cho phase1/start.py với 3 mode: train | create | predict
# ==========================================================

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the current time with the format y-m-d_h-m-s
CURRENT_TIME=$(date +"%Y-%m-%d_%H-%M-%S")

echo -e "${GREEN}$CURRENT_TIME.${NC}"
echo -e "${GREEN}Checking arguments...${NC}"

# Check if ROOT_WS_DUY environment variable is set
if [ -z "$ROOT_WS_DUY" ]; then
    echo -e "${RED}Environment variable ROOT_WS_DUY is not set. Please set it before running the script.${NC}"
    exit 1
fi

# --- Default values ---
colab=false
mode=""
input_folder=""
output_folder=""
predict_folder=""
training_json=""
noh=""
epochs=""
model_path=""
skip_prepare=false

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
  case $1 in
    -m|--mode) mode="$2"; shift 2 ;;
    -i|--input) input_folder="$2"; shift 2 ;;
    -o|--output) output_folder="$2"; shift 2 ;;
    -p|--predict) predict_folder="$2"; shift 2 ;;
    -j|--trainj) training_json="$2"; shift 2 ;;
    -n|--noh) noh="$2"; shift 2 ;;
    -e|--epochs) epochs="$2"; shift 2 ;;
    -mp|--model_path) model_path="$2"; shift 2 ;;
    --skip_prepare) skip_prepare=true; shift ;;
    -c|--colab) colab="$2"; shift 2 ;;
    *) echo -e "${RED}Unknown argument: $1${NC}"; exit 1 ;;
  esac
done

# --- Check mode ---
if [ -z "$mode" ]; then
    echo -e "${YELLOW}Usage: $0 -m [train|create|predict] [options]${NC}"
    exit 1
fi

echo -e "${GREEN}Change to the working directory...${NC}"
cd "$ROOT_WS_DUY/ThesisMaster" || exit 1

# --- Activate Conda ---
if [ "$colab" != "true" ]; then
    echo -e "${GREEN}Activating Conda environment 'thesis-master'...${NC}"
    source ~/miniconda3/etc/profile.d/conda.sh
    conda activate thesis-master
fi

# --- Logging setup ---
SCRIPT_DIR="${ROOT_WS_DUY}/ThesisMaster/scripts"
LOG_DIR="${SCRIPT_DIR}/logs"
LOG_FILE="$LOG_DIR/output_$CURRENT_TIME.log"

mkdir -p "$LOG_DIR"

# --- Build command ---
case $mode in
  train)
    if [ -z "$input_folder" ] || [ -z "$output_folder" ] || [ -z "$training_json" ] || [ -z "$noh" ]; then
        echo -e "${RED}Train mode requires: -i, -o, -j, -n${NC}"
        exit 1
    fi
    cmd="python3 -u phase1/start.py -i \"$input_folder\" -o \"$output_folder\" -trainj \"$training_json\" -noh $noh"
    [ -n "$epochs" ] && cmd="$cmd -e $epochs"
    [ -n "$predict_folder" ] && cmd="$cmd -p \"$predict_folder\""
    ;;
  create)
    if [ -z "$input_folder" ] || [ -z "$output_folder" ] || [ -z "$noh" ]; then
        echo -e "${RED}Create mode requires: -i, -o, -n${NC}"
        exit 1
    fi
    cmd="python3 -u phase1/start.py -i \"$input_folder\" -o \"$output_folder\" -noh $noh -omd"
    ;;
  predict)
    if [ -z "$model_path" ] || [ -z "$predict_folder" ]; then
        echo -e "${RED}Predict mode requires: -mp, -p${NC}"
        exit 1
    fi
    cmd="python3 -u phase1/start.py -pred_only -mp \"$model_path\" -p \"$predict_folder\""
    $skip_prepare && cmd="$cmd --skip_prepare_predict_data"
    ;;
  *)
    echo -e "${RED}Invalid mode: $mode${NC}"
    exit 1
    ;;
esac

# --- Run command ---
echo -e "${GREEN}Running: $cmd${NC}"
eval $cmd 2>&1 | tee "$LOG_FILE"

# --- Deactivate Conda ---
if [ "$colab" != "true" ]; then
    conda deactivate
fi

echo -e "${YELLOW}Logging to $LOG_FILE.${NC}"
echo -e "${GREEN}End python script.${NC}"

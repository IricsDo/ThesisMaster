#!/bin/bash
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

# Check if arguments are passed
if [ "$#" -lt 4 ]; then
    echo -e "${YELLOW}Usage: $0 -i input_folder -o output_folder [-colab true|false]${NC}"
    exit 1
fi

# Default value for colab argument
colab=false

# Parse the input arguments
while getopts ":i:o:c:" opt; do
  case $opt in
    i) input_folder="$OPTARG"
    ;;
    o) output_folder="$OPTARG"
    ;;
    c) colab="$OPTARG"
    ;;
    \?) echo -e "${RED}Invalid option -$OPTARG${NC}" >&2
        exit 1
    ;;
  esac
done

echo -e "${GREEN}Change to the working directory...${NC}"
cd "$ROOT_WS_DUY/ThesisMaster" || exit  # Ensure the folder exists

# Change to the directory where your Python code resides
ROOT_WS_DUY="${ROOT_WS_DUY:?Environment variable ROOT_WS_DUY is not set}"

# Activate Conda environment if colab is false
if [ "$colab" != "true" ]; then
    echo -e "${GREEN}Activating Conda environment 'thesis-master'...${NC}"
    source ~/miniconda3/etc/profile.d/conda.sh  # Adjust the path if necessary
    conda activate thesis-master
fi

SCRIPT_DIR="${ROOT_WS_DUY}/ThesisMaster/scripts"
LOG_DIR="${SCRIPT_DIR}/logs"
LOG_FILE="$LOG_DIR/output_$CURRENT_TIME.log"

# Check if the log directory exists; if not, create it
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
    echo "Created log directory: $LOG_DIR"
fi

echo -e "${GREEN}Running command ...${NC}"
# Run the Python script with the provided arguments
python3 phase1/start.py -i "$input_folder" -o "$output_folder" -v 2>&1 | tee "$LOG_FILE"

# Deactivate the environment if it was activated
if [ "$colab" != "true" ]; then
    conda deactivate
fi

echo -e "${YELLOW}Logging to $LOG_FILE.${NC}"
echo -e "${GREEN}End python script.${NC}"

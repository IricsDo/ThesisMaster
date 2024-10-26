#!/bin/bash
# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color


# Get the current time with the format y-m-d_h-m-s
CURRENT_TIME=$(date +"%Y-%m-%d_%H-%M-%S")

echo -e "${GREEN}Start python script.${NC}"

# Check if root_dir environment variable is set
if [ -z "$ROOT_DIR" ]; then
    echo -e "${RED}Environment variable ROOT_DIR is not set. Please set it before running the script.${NC}"
    exit 1
fi

# Check if two arguments are passed
if [ "$#" -ne 4 ]; then
    echo -e "${YELLOW}Usage: $0 -i input_folder -o output_folder${NC}"
    exit 1
fi

# Parse the input arguments
while getopts ":i:o:" opt; do
  case $opt in
    i) input_folder="$OPTARG"
    ;;
    o) output_folder="$OPTARG"
    ;;
    \?) echo -e "${RED}Invalid option -$OPTARG${NC}" >&2
        exit 1
    ;;
  esac
done

# Change to the directory where your Python code resides
ROOT_DIR="${ROOT_DIR:?Environment variable ROOT_DIR is not set}"
SCRIPT_DIR="${ROOT_DIR}/scripts"
cd "$SCRIPT_DIR" || exit  # Ensure the folder exists

# Activate Conda environment
echo -e "${GREEN}Activating Conda environment 'thesis-master'...${NC}"
source ~/anaconda3/etc/profile.d/conda.sh  # Adjust the path if necessary
conda activate thesis-master

LOG_DIR="${SCRIPT_DIR}/logs"
LOG_FILE="$LOG_DIR/output_$CURRENT_TIME.log"

# Run the Python script with the provided arguments
python3 phase1/start.py -i "$input_folder" -o "$output_folder" 2>&1 | tee "$LOG_FILE"

# Deactivate the environment (optional, but a good practice)
conda deactivate

echo "Start time: $CURRENT_TIME" > "Logging to $LOG_FILE"

echo -e "${GREEN}End python script.${NC}"

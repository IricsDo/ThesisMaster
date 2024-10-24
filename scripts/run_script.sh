#!/bin/bash
# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Start python script.${NC}"

# Check if script_dir environment variable is set
if [ -z "$SCRIPT_DIR" ]; then
    echo -e "${RED}Environment variable SCRIPT_DIR is not set. Please set it before running the script.${NC}"
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
SCRIPT_DIR="${SCRIPT_DIR:?Environment variable SCRIPT_DIR is not set}"
SCRIPT_DIR="${SCRIPT_DIR}/scripts"
cd "$SCRIPT_DIR" || exit  # Ensure the folder exists

# Run the Python script with the provided arguments
python3 phase1/start.py -i "$input_folder" -o "$output_folder"

echo -e "${GREEN}End python script.${NC}"
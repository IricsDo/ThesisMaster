#!/bin/bash

export CUDA_VISIBLE_DEVICES=""
export OMP_NUM_THREADS=4  # Set to the number of physical cores
export TF_INTRA_OP_PARALLELISM_THREADS=4
export TF_INTER_OP_PARALLELISM_THREADS=2

# setup.sh - Setup Conda environment for Thesis Master

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check ROOT_WS_DUY
if [ -z "$ROOT_WS_DUY" ]; then
    echo -e "${RED}Environment variable ROOT_WS_DUY is not set. Please set it before running this script.${NC}"
    echo -e "${YELLOW}Example:${NC} export ROOT_WS_DUY=/path/to/workspace"
    exit 1
fi

echo -e "${GREEN}ROOT_WS_DUY detected: $ROOT_WS_DUY${NC}"

# Ensure conda is available
if ! command -v conda &> /dev/null; then
    echo -e "${RED}conda not found. Please install Miniconda or Anaconda before running this script.${NC}"
    exit 1
fi

# Navigate to ThesisMaster folder
cd "$ROOT_WS_DUY/ThesisMaster" || { echo -e "${RED}ThesisMaster folder not found in $ROOT_WS_DUY${NC}"; exit 1; }

# Check if environment file exists
if [ ! -f "environment.yaml" ]; then
    echo -e "${RED}environment.yaml not found in ThesisMaster directory.${NC}"
    exit 1
fi

# Remove existing environment if it exists
if conda info --envs | grep -q "thesis-master"; then
    echo -e "${YELLOW}Environment thesis-master already exists. Removing it...${NC}"
    conda env remove -n thesis-master
fi

# Create new environment
echo -e "${GREEN}Creating conda environment 'thesis-master' from environment.yaml...${NC}"
conda env create -n thesis-master -f environment.yaml

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Environment thesis-master successfully created!${NC}"
    echo -e "${YELLOW}To activate it, run:${NC} conda activate thesis-master"
else
    echo -e "${RED}Failed to create environment thesis-master.${NC}"
    exit 1
fi

#!/bin/bash

export ROOT_WS_DUY=/media/hoanguyen/0AFECAD26E04553D/DoDuy-Working-Space
export CUDA_VISIBLE_DEVICES=""
export OMP_NUM_THREADS=4  # Set to the number of physical cores
export TF_INTRA_OP_PARALLELISM_THREADS=4
export TF_INTER_OP_PARALLELISM_THREADS=2
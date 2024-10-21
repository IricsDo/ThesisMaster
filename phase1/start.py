from phase1.core_phase.step_1.data_scanning import scan
from phase1.core_phase.step_1.data_creation import creation
from phase1.core_phase.step_1.data_combine import combine
from phase1.core_phase.step_2.setup_json import setup_training_input
from phase1.core_phase.step_3.plot_error import plot_loss
from phase1.core_phase.step_3.train_model import train
from phase1.core_phase.step_4.model_compress import compress
from phase1.core_phase.step_4.test_model import test
from phase1.core_phase.step_4.valid_model import vaild

import argparse
import os

def step1(data_directory : str, new_directory : str) -> None:
    folders = scan(data_directory)
    train_val_folders = creation(new_directory, folders)
    combine(new_directory, train_val_folders)

def step2() -> None:
    source_file =r'E:\Work Spaces\Thesis\Code\Thes, isMaster\phase1\config\input.json'
    new_file = r'E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out\input.json'
    type_map_value = ["C", "H"]  
    training_systems = [r"E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out\training_data"]  
    validation_systems = [r"E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out\validation_data"] 
    disp_file_value = r'E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out\lcurve.out'
    setup_training_input(source_file, new_file, type_map_value, training_systems, validation_systems, disp_file_value)


def step3(new_directory : str) -> None:
    train(new_directory)
    plot_loss(new_directory)


def step4(new_directory : str) -> None:
    compress(new_directory)
    test(new_directory)
    vaild(new_directory)

def main():
    # Create an ArgumentParser object with a custom description
    parser = argparse.ArgumentParser(description="A script to parse folder paths from terminal with verbose option and help support.")
    
    # Add arguments for input and output folders (required)
    parser.add_argument('-i', '--input_folder', type=str, required=True, help="The input folder to process.")
    parser.add_argument('-o', '--output_folder', type=str, required=True, help="The output folder where results will be saved.")

    # Add optional verbose argument
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose mode for detailed output.")
    
    # Add help flag (this is optional because argparse automatically includes it)
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit.')

    # Parse the arguments
    args = parser.parse_args()

    # Verbose mode check
    if args.verbose:
        print("Verbose mode is enabled.")
    
    # Check if the input folder exists
    if not os.path.isdir(args.input_folder):
        print(f"Error: Input folder '{args.input_folder}' does not exist.")
        return
    
    # Check if the output folder exists, create it if it doesn't
    if not os.path.isdir(args.output_folder):
        print(f"Output folder '{args.output_folder}' does not exist. Creating it...")
        os.makedirs(args.output_folder)

    # If verbose, print the folder paths
    if args.verbose:
        print(f"Input folder: {args.input_folder}")
        print(f"Output folder: {args.output_folder}")
    
if __name__ == "__main__":
    main()

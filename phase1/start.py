import sys
import os
sys.path.append(os.getcwd())
import traceback
import argparse
import os

from utils_com.logger import ServerLogger
LOGGER = ServerLogger()

LOGGER.log(f'Import library...')
try:
    from core_phase.step_1.data_scanning import scan
    from core_phase.step_1.data_creation import creation
    from core_phase.step_1.data_combine import combine
    from core_phase.step_2.setup_json import setup_training_input
    from core_phase.step_3.plot_error import plot_loss
    from core_phase.step_3.train_model import train
    from core_phase.step_4.model_compress import compress
    from core_phase.step_4.test_model import test
    from core_phase.step_4.valid_model import vaild
    from utils_com.traceback_func import run_with_traceback
    from config.return_code import ReturnCode

except Exception as e:
    traceback.print_exc()
    LOGGER.log(f'An error occurred: {e}')
    exit(-1)

LOGGER.log(f'Import library success')

def step1(data_directory : str, new_directory : str) -> None:
    folders = scan(data_directory)
    train_val_folders = creation(new_directory, folders)
    combine(new_directory, train_val_folders)

def step2(new_directory : str) -> None:
    source_training_file = os.path.abspath(os.path.join('phase1', 'config', 'input.json'))
    new_training_file = os.path.join(new_directory, 'input.json')
    type_map_value = ["Si", "C", "H"]  
    training_systems = [os.path.join(new_directory, 'training_data')]  
    validation_systems = [os.path.join(new_directory, 'validation_data')] 
    disp_file_value = os.path.join(new_directory, 'lcurve.out')
    numb_steps = 1000
    setup_training_input(source_training_file, new_training_file, type_map_value, training_systems, validation_systems, disp_file_value, numb_steps)


def step3(new_directory : str) -> None:
    train(new_directory)
    plot_loss(new_directory) 

def step4(new_directory : str) -> None:
    compress(new_directory)
    test(new_directory)
    vaild(new_directory)

def workflow(input_folder : str, output_folder : str, verbose : bool) -> int:

    LOGGER.log("\n***Step 1/4 in phase 1 on running!\n")
    if(run_with_traceback(step1, input_folder, output_folder)):
        return ReturnCode.ERROR_CODE_1
    else:
        LOGGER.log("\n***Step 1/4 in phase 1 run successfully!\n")

    LOGGER.log("\n***Step 2/4 in phase 1 on running!\n")
    if(run_with_traceback(step2, output_folder)):
        return ReturnCode.ERROR_CODE_2
    else:
        LOGGER.log("\n***Step 2/4 in phase 1 run successfully!\n")

    LOGGER.log("\n***Step 3/4 in phase 1 on running!\n")
    if(run_with_traceback(step3, output_folder)):
        return ReturnCode.ERROR_CODE_3
    else:
        LOGGER.log("\n***Step 3/4 in phase 1 run successfully!\n")

    LOGGER.log("\n***Step 4/4 in phase 1 on running!\n")
    if(run_with_traceback(step4, output_folder)):
        return ReturnCode.ERROR_CODE_4
    else:
        LOGGER.log("\n***Step 4/4 in phase 1 run successfully!\n")

    LOGGER.log("Phase 1 run successfully!")
    return ReturnCode.SUCCESS

def main():
    # Create an ArgumentParser object with a custom description
    parser = argparse.ArgumentParser(description="A script to parse folder paths from terminal with verbose option and help support.")
    
    # Add arguments for input and output folders (required)
    parser.add_argument('-i', '--input_folder', type=str, required=True, help="The input folder to process.")
    parser.add_argument('-o', '--output_folder', type=str, required=True, help="The output folder where results will be saved.")

    # Add optional verbose argument
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose mode for detailed output.")
    
    # Parse the arguments
    args = parser.parse_args()

    # Verbose mode check
    if args.verbose:
        LOGGER.log("Verbose mode is enabled.")
    
    # Check if the input folder exists
    if not os.path.isdir(args.input_folder):
        LOGGER.log(f"Error: Input folder '{args.input_folder}' does not exist.")
        return
    
    # Check if the output folder exists, create it if it doesn't
    if not os.path.isdir(args.output_folder):
        LOGGER.log(f"Output folder '{args.output_folder}' does not exist. Creating it...")
        os.makedirs(args.output_folder)

    # If verbose, print the folder paths
    if args.verbose:
        print(f"Input folder: {args.input_folder}")
        print(f"Output folder: {args.output_folder}")


    state = workflow(args.input_folder, args.output_folder, args.verbose)
    LOGGER.log(f'State of workflow phase 1: {ReturnCode.get_message(state)}')
    LOGGER.log(f'\nServer shutdown, bye!\n')

    
if __name__ == "__main__":
    LOGGER.log(f'\nServer starting, hi!\n')
    try:
        main()
    except SystemExit as e:
        print('\n')
        LOGGER.log(f'An error occurred: {e} => Missing input arguments')

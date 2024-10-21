import argparse
import os

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

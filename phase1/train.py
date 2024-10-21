
import subprocess

def execute_command(command):
    try:
        # Run the command and capture both stdout and stderr
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True
        )
        # Store the output in a variable
        output = result.stdout
        return output, None
    except subprocess.CalledProcessError as e:
        # Handle the error and store the stderr
        return None, e.stderr

if __name__ =='__main__':
    # Example usage
    # !dp train input.json
    command = "ls -la"  # Replace with your command
    output, error = execute_command(command)

    if output:
        print("Output:\n", output)
    if error:
        print("Error:\n", error)



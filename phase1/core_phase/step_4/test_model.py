from utils_com.logger import ServerLogger
from utils.exec_command import execute_command

def test(new_directory: str, verbose: bool = False) -> None:
    LOGGER = ServerLogger()
    # command = "dp test -m graph.pb -s validation_data"
    command = "dir"
    output, error = execute_command(command, new_directory)
    if verbose:
        LOGGER.log(f"Test output: {output}")
    if error:
        LOGGER.log(f"Test error: {error}")
        raise Exception('Have the error in test command')

if __name__ == '__main__':

    # Step 4.2
    new_directory = r'E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out'
    test(new_directory)
from utils.exec_command import execute_command
from utils_com.logger import ServerLogger


def freeze(new_directory: str, verbose: bool = False) -> None:
    LOGGER = ServerLogger()
    command = f"dp freeze -o graph.pb"
    # command = "dir"
    output, error = execute_command(command, new_directory)
    if verbose:
        LOGGER.log(f"Compress output: {output}")
        LOGGER.log(f"Compress error: {error}")
    if not error and not output:
        raise Exception("Have the error in compress command")


def compress(new_directory: str, verbose: bool = False) -> None:
    LOGGER = ServerLogger()
    command = f"dp compress -i graph.pb -o compress.pb"
    # command = "dir"
    output, error = execute_command(command, new_directory)
    if verbose:
        LOGGER.log(f"Compress output: {output}")
        LOGGER.log(f"Compress error: {error}")
    if not error and not output:
        raise Exception("Have the error in compress command")


if __name__ == "__main__":

    # Step 4.1
    new_directory = r"E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out"
    compress(compress)

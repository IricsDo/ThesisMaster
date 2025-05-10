from utils_com.logger import ServerLogger
from utils.exec_command import execute_command


def test(new_directory: str, tesorflow_fw: bool = True, pytorch_fw: bool = False, verbose: bool = False) -> None:
    LOGGER = ServerLogger()
    if tesorflow_fw:
        command = "dp --tf test -m graph.pb -s validation_data"
    elif pytorch_fw:
        command = "dp --pt test -m graph.pb -s validation_data"
    else:
        raise Exception("Backend not vaild!")
    # command = "dir"
    output, error = execute_command(command, new_directory)
    if verbose:
        LOGGER.log(f"Test output: {output}")
        LOGGER.log(f"Test error: {error}")
    if not error and not output:
        raise Exception("Have the error in test command")


if __name__ == "__main__":

    # Step 4.2
    new_directory = r"E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out"
    test(new_directory)

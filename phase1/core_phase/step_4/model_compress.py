from utils.exec_command import execute_command
from utils_com.logger import ServerLogger


def freeze(
    new_directory: str, tesorflow_fw: bool, pytorch_fw: bool, verbose: bool = False
) -> None:
    LOGGER = ServerLogger()

    if tesorflow_fw:
        command = f"dp --tf freeze -o graph.pb"
    elif pytorch_fw:
        command = f"dp --pt freeze -o graph.pth"
    else:
        raise Exception("Backend not vaild!")
    # command = "dir"
    output, error = execute_command(command, new_directory)
    if verbose:
        LOGGER.log(f"Compress output: {output}")
        LOGGER.log(f"Compress error: {error}")
    if not error and not output:
        raise Exception("Have the error in compress command")


def compress(
    new_directory: str, tesorflow_fw: bool, pytorch_fw: bool, verbose: bool = False
) -> None:
    LOGGER = ServerLogger()

    if tesorflow_fw:
        command = f"dp --tf compress -i graph.pb -o compress.pb"
    elif pytorch_fw:
        command = f"dp --pt compress -i graph.pth -o compress.pth"
    else:
        raise Exception("Backend not vaild!")

    # command = "dir"
    output, error = execute_command(command, new_directory)
    if verbose:
        LOGGER.log(f"Compress output: {output}")
        LOGGER.log(f"Compress error: {error}")
    if not error and not output:
        raise Exception("Have the error in compress command")

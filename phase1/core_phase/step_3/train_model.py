import os

from utils_com.logger import ServerLogger
from utils.exec_command import execute_command


def train(
    new_directory: str,
    tesorflow_fw: bool = True,
    pytorch_fw: bool = False,
    verbose: bool = False,
) -> None:
    LOGGER = ServerLogger()
    if tesorflow_fw:
        command = f"dp --tf train input.json"
    elif pytorch_fw:
        command = f"dp --pt train input.json"
    else:
        raise Exception("Backend not vaild!")
    # command = "dir"
    output, error = execute_command(command, new_directory)
    if verbose:
        LOGGER.log(f"Training output: {output}")
        LOGGER.log(f"Training error: {error}")
    if not error and not output:
        raise Exception("Have the error in train command")

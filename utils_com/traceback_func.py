import traceback

from utils_com.logger import ServerLogger


def run_with_traceback(func, *args, **kwargs) -> bool:
    """
    Wrapper function to run any code with a try-except block that captures traceback.

    Parameters:
    func : function
        The function to be executed inside try-except block.
    *args : list
        Positional arguments for the function.
    **kwargs : dict
        Keyword arguments for the function.

    Returns:
    The return value of the function if it succeeds, or the traceback if it fails.
    """
    LOGGER = ServerLogger()
    error = False
    try:
        # Execute the function with arguments
        return func(*args, **kwargs)
    except Exception as e:
        # Store the traceback in a variable and return it
        error_traceback = traceback.format_exc()
        LOGGER.log(f"\nAn error occurred: {e}")
        LOGGER.log(f"\nTraceback: {error_traceback}")
        error = True
    return error

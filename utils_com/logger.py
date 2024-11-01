import os
import logging
from datetime import datetime

import os
import logging
from threading import Lock
from datetime import datetime


class SingletonMeta(type):
    """A thread-safe Singleton implementation using metaclass."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class ServerLogger(metaclass=SingletonMeta):
    _lock = Lock()  # Thread lock for folder creation

    def __init__(self, log_dir="logs") -> None:
        self.log_dir = log_dir
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self._create_log_folder()  # Initial log folder setup

    def _create_log_folder(self) -> None:
        """Create a new log folder based on the current date and time."""
        with self._lock:  # Ensure folder creation is thread-safe
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.folder_path = os.path.join(self.log_dir, current_time)
            os.makedirs(self.folder_path, exist_ok=True)
            log_file = os.path.join(self.folder_path, "log.txt")

            # Clear existing handlers to avoid duplicate logs
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)

            # Configure logging to use the new log file and also print to console
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                handlers=[
                    logging.FileHandler(log_file),  # Write to log file
                    logging.StreamHandler(),  # Print to terminal
                ],
            )
            self.logger = logging.getLogger()

    def log(self, message: str) -> None:
        """Thread-safe log method. Checks for new day and creates new folder if needed."""
        new_date = datetime.now().strftime("%Y-%m-%d")
        if new_date != self.current_date:
            with self._lock:  # Ensure thread-safe folder creation on new day
                if new_date != self.current_date:  # Double check within lock
                    self.current_date = new_date
                    self._create_log_folder()

        # Log the message with the current timestamp to both file and console
        self.logger.info(message)


# Example usage
if __name__ == "__main__":
    logger = ServerLogger()
    logger.log("This is a log message.")
    logger.log("Logging another message.")

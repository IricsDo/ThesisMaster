import os
import logging
from datetime import datetime

import os
import logging
from threading import Lock
from datetime import datetime


from threading import Lock

class SingletonMeta(type):
    """Thread-safe Singleton metaclass."""
    _instances = {}
    _instances_lock = Lock() # Lock for thread-safe singleton creation

    def __call__(cls, *args, **kwargs): 
        # Fast path : Already created instance 
        if cls in cls._instances:
            return cls._instances[cls]

        # Slow path: Need to create instance safely
        with SingletonMeta._instances_lock:
            # Double-check in lock to avoid race condition creation of multiple instances
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance

        return cls._instances[cls]



class ServerLogger(metaclass=SingletonMeta):
    _folder_lock = Lock()  # Thread lock for folder creation

    def __init__(self, log_dir: str | None = None):
        # Prevent re-initialization in singleton
        if hasattr(self, "_initialized") and self._initialized:
            return

        # Initialize logger
        self.log_dir = (log_dir.strip() if log_dir and log_dir.strip() else "logs")
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self._create_log_folder()
        self._initialized = True

    def _create_log_folder(self) -> None:
        with self._folder_lock:
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.folder_path = os.path.join(self.log_dir, current_time)
            os.makedirs(self.folder_path, exist_ok=True)

            log_file = os.path.join(self.folder_path, "log.txt")

            # Set up logger
            self.logger = logging.getLogger("server_logger")
            self.logger.setLevel(logging.INFO)
            self.logger.propagate = False

            # Clear handler if already exists
            for h in list(self.logger.handlers):
                self.logger.removeHandler(h)
                h.close()

            formatter = logging.Formatter(
                fmt="%(asctime)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setFormatter(formatter)

            sh = logging.StreamHandler()
            sh.setFormatter(formatter)

            self.logger.addHandler(fh)
            self.logger.addHandler(sh)


    def set_log_dir(self, log_dir: str | None) -> None:
        new_dir = (log_dir.strip() if log_dir and log_dir.strip() else "logs")
        if new_dir != self.log_dir:
            self.log_dir = new_dir
            self._create_log_folder()

    def log(self, message: str) -> None:
        """Thread-safe log method. Checks for new day and creates new folder if needed."""
        new_date = datetime.now().strftime("%Y-%m-%d")
        if new_date != self.current_date:
            with self._folder_lock:  # Ensure thread-safe folder creation on new day
                if new_date != self.current_date:  # Double check within lock
                    self.current_date = new_date
                    self._create_log_folder()

        # Log the message with the current timestamp to both file and console
        self.logger.info(message)

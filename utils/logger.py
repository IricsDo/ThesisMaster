import os
import logging
from datetime import datetime

class SingletonLogger:
    _instance = None

    def __new__(cls, log_directory=None):
        if cls._instance is None:
            cls._instance = super(SingletonLogger, cls).__new__(cls)
            cls._instance._initialize(log_directory)
        return cls._instance

    def _initialize(self, log_directory):
        # Set the log directory; if not provided, use the current working directory
        self.log_directory = log_directory if log_directory else os.getcwd()

        # Initialize the log file for the current day
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self._setup_logger()

    def _setup_logger(self):
        # Create directory for today's date
        date_directory = os.path.join(self.log_directory, self.current_date)

        # Create the directory if it doesn't exist
        os.makedirs(date_directory, exist_ok=True)

        # Set up the log file path
        self.log_file = os.path.join(date_directory, 'log.txt')

        # Configure logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.DEBUG,
            format='%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def log(self, message):
        # Check if the date has changed
        today = datetime.now().strftime("%Y-%m-%d")
        if today != self.current_date:
            self.current_date = today
            self._setup_logger()  # Reconfigure for the new day

        # Log the message to the file
        logging.debug(message)

        # Print the message to the terminal
        print(message)

    @classmethod
    def log_message(cls, message):
        """ Class method to log messages directly """
        logger = cls()  # Get the singleton instance
        logger.log(message)

# Example usage
if __name__ == "__main__":
    # Pass a custom directory where you want to store the log files
    log_directory = r'E:\Work Spaces\Thesis\Code\ThesisMaster\log'  # Example path
    logger = SingletonLogger(log_directory)
    logger.log_message("This is a log message.")
    logger.log_message("Logging another message.")

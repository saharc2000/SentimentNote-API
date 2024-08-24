import logging

class Logger:
    def __init__(self, name: str, log_file: str = "app.log", level: int = logging.INFO):
        """
        Initialize the logger with the specified name, log file, and log level.

        :param name: The name of the logger.
        :param log_file: The file to log messages to. Default is 'app.log'.
        :param level: The logging level. Default is logging.INFO.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        # Log format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add the handler to the logger
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

# Initialize the logger
logger = Logger(__name__).get_logger()

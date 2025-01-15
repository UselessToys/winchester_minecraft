import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Configures and returns a logger with the specified name.

    The logger will output to the console with the following format:
    %(asctime)s - %(name)s - %(levelname)s - %(message)s

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The configured logger.
    """
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG

    # Create a console handler and set its level to DEBUG
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # Add the handler to the logger
    if not logger.handlers:
        logger.addHandler(handler)

    return logger
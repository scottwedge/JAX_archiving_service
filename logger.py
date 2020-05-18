import logging
import os

LOGGER_FILE_NAME = "JAS_log"  # name for the log file in /logs
DEFAULT_LEVEL = "DEBUG"


def get_logger_for_string(*, logger_name: str, level: str):
    """
    :description: A mapping function from strings to logging levels.
    :param logger_name: Name of the logger handle e.g. `stream_handle`.
    :param level: The string describing the logging level to set.
    """
    switcher = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return switcher.get(
        level,
        f"{logger_name} logging level is not one of "
        + "[DEBUG, INFO, WARNING, ERROR, CRITICAL]",
    )


def generate_logger(
    *,
    name: str = LOGGER_FILE_NAME,
    logging_level: str = DEFAULT_LEVEL,
    format_string: str = ("%(message)s"),
):
    """
    :description: Creates a logger as desired for the global namespace without
    polluting the global namespace.

    :param name: The name of the logger.
    :param logging_level: The logging level to record to the logging file.
    :param format_string: A string to be passed to Python's logger generator
    facility to format logging output.
    :returns: A usable and proper Python logger.
    """
    logging_level = get_logger_for_string(logger_name=name, level=logging_level)

    logger = logging.getLogger(name)
    logger.setLevel(logging_level)

    # create console handler with a higher log level
    os.makedirs("logs", exist_ok=True)
    file_handle = logging.FileHandler(f"logs/{name}.log")
    file_handle.setLevel(logging_level)
    # create formatter and add it to the handlers
    log_format = logging.Formatter(format_string)
    file_handle.setFormatter(log_format)
    logger.addHandler(file_handle)
    return logger


LOGGER = None

if not LOGGER:
    LOGGER = generate_logger()

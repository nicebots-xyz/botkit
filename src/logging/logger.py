import logging
from typing import Optional
from ..config import config


def get_logger(*, name: Optional[str] = None) -> logging.Logger:
    """
    This function is used to get a logger with a specific name and level.

    Parameters:
    name (str, optional): The name of the logger. If no name is provided, the name of the current module is used.

    Returns:
    logging.Logger: A logger with the specified name and level. The level is retrieved from the configuration file.
    If no level is specified in the configuration file, the default level is INFO.
    """
    logger_name = name or __name__
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, config["logging"]["level"].upper() or "INFO"))
    return logger
import logging
import os
import time

from ..config import config


level: int = getattr(
    logging, config.get("logging", {}).get("level", "").upper() or "INFO"
)
logging.basicConfig(level=level, handlers=[])


class ColoredFormatter(logging.Formatter):
    prefix = "\033["
    suffix = "\033[0m"
    fmt = "%(levelname)s: %(message)s (%(filename)s:%(lineno)d)"

    COLORS = {
        "WARNING": 33,  # yellow
        "INFO": 37,  # white
        "DEBUG": 34,  # blue
        "CRITICAL": 31,  # red
        "ERROR": 31,  # red
    }

    def __init__(self, fmt=fmt, datefmt=None, style="%"):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def format(self, record):
        color = self.COLORS.get(record.levelname)
        message = super().format(record)
        if color:
            message = f"{self.prefix}{color}m{message}{self.suffix}"
        return message


os.makedirs("logs", exist_ok=True)
file_handler = logging.FileHandler(f"logs/{time.time()}.log", encoding="utf-8")
file_handler.setFormatter(
    logging.Formatter(
        "%(levelname)-8s at %(asctime)s: %(message)s\n\t%(pathname)s:%(lineno)d"
    )
)
file_handler.setLevel("DEBUG")

console_handler = logging.StreamHandler()
console_handler.setFormatter(
    ColoredFormatter("%(levelname)-8s %(module)-10s %(message)s")
)
console_handler.setLevel(level)


def patch(logger_: str | logging.Logger):
    if isinstance(logger_, str):
        logger_ = logging.getLogger(logger_)
    logger_.debug("")
    logger_.handlers = []  # Clear any existing handlers
    logger_.addHandler(file_handler)
    logger_.addHandler(console_handler)
    logger_.propagate = False
    logger_.setLevel(level)
    return logger_


# Configure discord logger
patch("discord")

# Configure application logger
logger = logging.getLogger("myapp")
logger.setLevel(level)
logger.handlers = []  # Clear any existing handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Prevent application logger from propagating to root logger
logger.propagate = False

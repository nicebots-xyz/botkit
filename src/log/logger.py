# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import logging
import os
import time
import coloredlogs

from src.config import config

# Define custom success level
SUCCESS = 31  # Between WARNING (30) and ERROR (40)
logging.addLevelName(SUCCESS, "SUCCESS")


class CustomLogger(logging.Logger):
    def success(self, msg, *args, **kwargs) -> None:  # pyright: ignore[reportUnknownParameterType,reportMissingParameterType]
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, msg, args, **kwargs)  # pyright: ignore[reportUnknownArgumentType]


# Register the custom logger class
logging.setLoggerClass(CustomLogger)

level: int = getattr(
    logging, config.get("logging", {}).get("level", "").upper() or "INFO"
)
logging.basicConfig(level=level, handlers=[])

os.makedirs("logs", exist_ok=True)
file_handler = logging.FileHandler(f"logs/{time.time()}.log", encoding="utf-8")
file_handler.setFormatter(
    logging.Formatter(
        "%(levelname)-8s at %(asctime)s: %(message)s\n\t%(pathname)s:%(lineno)d"
    )
)
file_handler.setLevel("DEBUG")

# More stylish coloredlogs format
fmt = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
date_fmt = "%Y-%m-%d %H:%M:%S"

# Custom level styles including SUCCESS
level_styles = {
    "spam": {"color": 22},
    "debug": {"color": 28},
    "verbose": {"color": 34},
    "notice": {"color": 220},
    "warning": {"color": 202},
    "success": {"color": 118, "bold": True},
    "error": {"color": 124},
    "critical": {"background": "red"},
}


def patch(logger_: str | logging.Logger) -> logging.Logger:
    if isinstance(logger_, str):
        logger_ = logging.getLogger(logger_)
        if not logger_:
            raise ValueError("Logger does not exist")
    logger_.debug("")
    logger_.handlers = []  # Clear any existing handlers
    logger_.addHandler(file_handler)
    logger_.propagate = False
    logger_.setLevel(level)
    coloredlogs.install(
        level=level,
        logger=logger_,
        fmt=fmt,
        datefmt=date_fmt,
        level_styles=level_styles,
    )
    return logger_


# Configure discord logger
patch("discord")

# Configure application logger
logger = logging.getLogger("bot")
patch(logger)
logger.setLevel(level)

# Prevent application logger from propagating to root logger
logger.propagate = False

logger: CustomLogger

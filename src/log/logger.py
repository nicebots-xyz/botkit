# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

import logging
import os
import time
from typing import Any

import coloredlogs

from src.config.models import LoggingConfig

# Define custom success level
SUCCESS = 31  # Between WARNING (30) and ERROR (40)
logging.addLevelName(SUCCESS, "SUCCESS")
logging.SUCCESS = SUCCESS  # pyright: ignore[reportAttributeAccessIssue]


class CustomLogger(logging.Logger):
    def success(self, msg: str, *args: object, **kwargs: Any) -> None:  # pyright: ignore[reportExplicitAny]
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, msg, args, **kwargs)


# Register the custom logger class
logging.setLoggerClass(CustomLogger)

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

_configured_level = logging.INFO
_configured_file_handler: logging.FileHandler | None = None
_patched_loggers: set[str] = set()


def patch(logger_: str | logging.Logger) -> logging.Logger:
    if isinstance(logger_, str):
        logger_ = logging.getLogger(logger_)
    logger_.handlers = []  # Clear any existing handlers
    if _configured_file_handler:
        logger_.addHandler(_configured_file_handler)
    logger_.propagate = False
    logger_.setLevel(_configured_level)
    _patched_loggers.discard(logger_.name)
    return logger_


def configure_logging(config: LoggingConfig) -> None:
    """Configure Botkit logging explicitly and idempotently."""
    global _configured_file_handler, _configured_level  # noqa: PLW0603

    _configured_level = getattr(logging, config.level.upper())
    logging.basicConfig(level=_configured_level, handlers=[], force=True)

    if _configured_file_handler:
        _configured_file_handler.close()
        _configured_file_handler = None

    if config.file:
        os.makedirs(config.directory, exist_ok=True)
        _configured_file_handler = logging.FileHandler(f"{config.directory}/{time.time()}.log", encoding="utf-8")
        _configured_file_handler.setFormatter(
            logging.Formatter("%(levelname)-8s at %(asctime)s: %(message)s\n\t%(pathname)s:%(lineno)d")
        )
        _configured_file_handler.setLevel("DEBUG")

    for logger_name in ("bot", "discord", "uvicorn", "uvicorn.error", "uvicorn.access", "uvicorn.asgi"):
        configured_logger = patch(logger_name)
        if config.console:
            coloredlogs.install(
                level=_configured_level,
                logger=configured_logger,
                fmt=fmt,
                datefmt=date_fmt,
                level_styles=level_styles,
            )
            _patched_loggers.add(logger_name)


# Configure application logger
def get_logger(name: str = "bot") -> CustomLogger:
    """Get a logger instance with CustomLogger type.

    Since we've set CustomLogger as the logger class via setLoggerClass,
    getLogger will return instances of CustomLogger.
    """
    return logging.getLogger(name)  # pyright: ignore[reportReturnType]


_logger_instance = get_logger("bot")

logger: CustomLogger = _logger_instance

# Prevent application logger from propagating to root logger
logger.propagate = False

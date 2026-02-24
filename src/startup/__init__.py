# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

"""Startup system for botkit.

This package provides a clean, type-safe interface for loading extensions
and starting the bot and/or backend server.
"""

from src.startup.backend import (
    run_startup_functions,
    setup_and_start_backend,
)
from src.startup.bot import setup_and_start_bot
from src.startup.loader import load_extensions

__all__ = [
    "load_extensions",
    "run_startup_functions",
    "setup_and_start_backend",
    "setup_and_start_bot",
]

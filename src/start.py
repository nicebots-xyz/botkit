# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

"""Main entry point for starting the bot and backend server.

This module provides the top-level orchestration for the startup process.
Most of the actual implementation has been moved to the src.startup package
for better organization and maintainability.
"""

import asyncio

from src.config import config
from src.log import logger
from src.startup import (
    load_extensions,
    run_startup_functions,
    setup_and_start_backend,
    setup_and_start_bot,
)
from src.startup.backend import create_backend_app, create_backend_bot
from src.utils import unzip_extensions


async def start(run_bot: bool | None = None, run_backend: bool | None = None) -> None:
    """Start the bot and/or backend server based on configuration.

    Args:
        run_bot: Whether to start the bot (defaults to config.use.bot)
        run_backend: Whether to start the backend server (defaults to config.use.backend)

    """
    if not config.bot.token:
        logger.critical("No bot token provided in config, exiting...")
        return

    if config.db.enabled:
        from src.database.config import init as init_db  # noqa: PLC0415

        logger.info("Initializing database...")
        await init_db()

    unzip_extensions()

    run_bot = run_bot if run_bot is not None else config.use.bot
    run_backend = run_backend if run_backend is not None else config.use.backend

    bot_functions, back_functions, startup_functions, translations = load_extensions()

    coros: list[asyncio.Task[None]] = []

    if bot_functions and run_bot:
        coros.append(asyncio.create_task(setup_and_start_bot(bot_functions, translations, config.bot)))

    if back_functions and run_backend:
        coros.append(asyncio.create_task(setup_and_start_backend(back_functions)))

    if not coros:
        logger.error("Nothing to start, exiting...")
        return

    if startup_functions:
        app = create_backend_app() if (back_functions and run_backend) else None
        bot = create_backend_bot() if (back_functions and run_backend) else None
        await run_startup_functions(startup_functions, app, bot)

    await asyncio.gather(*coros)

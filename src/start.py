# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

"""Main entry point for starting the bot and backend server.

This module provides the top-level orchestration for the startup process.
Most of the actual implementation has been moved to the src.startup package
for better organization and maintainability.
"""

import asyncio
import contextlib

from fastapi import FastAPI

from src import custom
from src.config import config
from src.config.models import BotConfig
from src.log import logger
from src.startup import load_extensions, run_startup_functions
from src.startup.backend import (
    create_backend_app,
    run_backend_only,
    serve_backend,
    setup_backend_extensions,
)
from src.startup.bot import create_bot, run_bot_connection, setup_bot, start_bot
from src.utils import unzip_extensions


async def run_bot_and_backend(
    bot: custom.Bot,
    app: FastAPI,
    bot_config: BotConfig,
) -> None:
    """Run the Discord gateway and backend API on one shared bot instance."""
    try:
        async with bot:  # https://github.com/Pycord-Development/pycord/issues/2958
            serve_task = asyncio.create_task(serve_backend(app, config.backend))
            try:
                await run_bot_connection(
                    bot,
                    bot_config.token,
                    bot_config.rest,
                    bot_config.public_key,
                )
            finally:
                serve_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await serve_task
    except Exception as e:  # noqa: BLE001
        logger.critical("An error occurred while running the bot and backend together.")
        logger.debug("", exc_info=e)


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

    start_bot_extensions = bool(bot_functions and run_bot)
    start_backend_server = bool(back_functions and run_backend)

    if not start_bot_extensions and not start_backend_server:
        logger.error("Nothing to start, exiting...")
        return

    app = None
    bot = create_bot(config.bot)
    if start_bot_extensions:
        setup_bot(bot, bot_functions, translations, config.bot)
    if start_backend_server:
        app = create_backend_app()
        setup_backend_extensions(app, bot, back_functions)

    if startup_functions:
        await run_startup_functions(startup_functions, app, bot)

    if start_bot_extensions and start_backend_server:
        if config.bot.rest:
            logger.critical(
                "REST bot mode and the Botkit backend cannot run together in one process. "
                "Disable bot.rest or use.backend."
            )
            return
        if app is None:
            logger.error("Backend app was not initialized, exiting...")
            return
        await run_bot_and_backend(bot, app, config.bot)
    elif start_bot_extensions:
        await start_bot(bot, config.bot.token, config.bot.rest, config.bot.public_key)
    elif app is None:
        logger.error("Backend app was not initialized, exiting...")
    else:
        await run_backend_only(app, bot, config.bot.token, config.backend)

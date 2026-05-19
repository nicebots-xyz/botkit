# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

"""Backend server initialization and startup logic."""

import asyncio
from typing import TYPE_CHECKING

import discord
import uvicorn
from fastapi import FastAPI

from src.config import config
from src.config.models import BackendConfig
from src.log import logger
from src.startup.types import StartupFunctionList, WebserverFunctionList
from src.utils import setup_func

if TYPE_CHECKING:
    from collections.abc import Awaitable


def create_backend_app() -> FastAPI:
    """Create a FastAPI application for the backend server.

    Returns:
        A configured FastAPI application instance

    """
    return FastAPI(title="Botkit Backend")


def create_backend_bot() -> discord.Bot:
    """Create a minimal Discord bot for the backend server.

    The backend server needs a bot instance for certain operations,
    but it doesn't need the full custom bot setup.

    Returns:
        A basic Discord bot with default intents

    """
    return discord.Bot(intents=discord.Intents.default())


def setup_backend_extensions(
    app: FastAPI,
    bot: discord.Bot,
    back_functions: WebserverFunctionList,
) -> None:
    """Set up all backend extensions.

    Args:
        app: The FastAPI application to configure
        bot: The Discord bot instance
        back_functions: List of (setup_webserver_function, config) tuples to execute

    """
    for function, its_config in back_functions:
        setup_func(function, app=app, bot=bot, config=its_config)


async def run_startup_functions(
    startup_functions: StartupFunctionList,
    app: FastAPI | None = None,
    bot: discord.Bot | None = None,
) -> None:
    """Run all registered startup functions concurrently.

    Args:
        startup_functions: List of (on_startup_function, config) tuples to execute
        app: Optional FastAPI application instance
        bot: Optional Discord bot instance

    """
    startup_coros: list[Awaitable[None]] = [  # pyright: ignore[reportUnknownVariableType]
        setup_func(function, app=app, bot=bot, config=its_config)  # pyright: ignore[reportCallIssue]
        for function, its_config in startup_functions
    ]
    await asyncio.gather(*startup_coros)


async def start_backend(app: FastAPI, bot: discord.Bot, token: str, backend_config: BackendConfig) -> None:
    """Start the backend server with Uvicorn.

    Args:
        app: The FastAPI application to serve
        bot: The Discord bot instance (for login)
        token: Discord bot token
        backend_config: Backend server settings

    """
    try:
        await bot.login(token)
        uvicorn_config = uvicorn.Config(
            app=app,
            host=backend_config.host,
            port=backend_config.port,
            access_log=backend_config.access_log,
            server_header=backend_config.server_header,
            log_config=None,
        )

        await uvicorn.Server(uvicorn_config).serve()
    except Exception as e:  # noqa: BLE001
        logger.critical("An error occurred while starting the backend server.")
        logger.debug("", exc_info=e)


async def setup_and_start_backend(
    back_functions: WebserverFunctionList,
) -> None:
    """Create, configure, and start the backend server.

    This is a convenience function that combines backend app creation,
    bot creation, extension setup, and server startup.

    Args:
        back_functions: List of (setup_webserver_function, config) tuples for extensions

    """
    app = create_backend_app()
    bot = create_backend_bot()
    setup_backend_extensions(app, bot, back_functions)
    await start_backend(app, bot, config.bot.token, config.backend)


__all__ = [
    "create_backend_app",
    "create_backend_bot",
    "run_startup_functions",
    "setup_and_start_backend",
    "setup_backend_extensions",
    "start_backend",
]

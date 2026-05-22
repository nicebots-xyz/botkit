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

    from src import custom


def create_backend_app() -> FastAPI:
    """Create a FastAPI application for the backend server.

    Returns:
        A configured FastAPI application instance

    """
    return FastAPI(title="Botkit Backend")


def create_backend_bot() -> "custom.Bot":
    """Create a bot for backend-only mode.

    Deprecated in favor of :func:`src.startup.bot.create_bot`, which applies cache
    and other bot configuration. Kept for backward compatibility.
    """
    from src.startup.bot import create_bot  # noqa: PLC0415

    return create_bot(config.bot)


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


def _uvicorn_config(app: FastAPI, backend_config: BackendConfig) -> uvicorn.Config:
    return uvicorn.Config(
        app=app,
        host=backend_config.host,
        port=backend_config.port,
        access_log=backend_config.access_log,
        server_header=backend_config.server_header,
        log_config=None,
    )


async def serve_backend(app: FastAPI, backend_config: BackendConfig) -> None:
    """Run the FastAPI app with Uvicorn (no Discord login)."""
    await uvicorn.Server(_uvicorn_config(app, backend_config)).serve()


async def run_backend_only(
    app: FastAPI,
    bot: discord.Bot,
    token: str,
    backend_config: BackendConfig,
) -> None:
    """Log in to Discord and serve the backend (backend-only mode)."""
    try:
        if not bot.user:
            await bot.login(token)
        await serve_backend(app, backend_config)
    except Exception as e:  # noqa: BLE001
        logger.critical("An error occurred while starting the backend server.")
        logger.debug("", exc_info=e)


async def start_backend(
    app: FastAPI,
    bot: discord.Bot,
    token: str,
    backend_config: BackendConfig,
    *,
    login: bool = True,
) -> None:
    """Start the backend server with Uvicorn.

    Args:
        app: The FastAPI application to serve
        bot: The Discord bot instance
        token: Discord bot token (used when ``login`` is True)
        backend_config: Backend server settings
        login: When True, log in before serving (backend-only). When False, the caller
            is responsible for authentication (combined bot + backend mode).

    """
    try:
        if login and not bot.user:
            await bot.login(token)
        await serve_backend(app, backend_config)
    except Exception as e:  # noqa: BLE001
        logger.critical("An error occurred while starting the backend server.")
        logger.debug("", exc_info=e)


async def setup_and_start_backend(
    back_functions: WebserverFunctionList,
    bot: "custom.Bot | None" = None,
) -> None:
    """Configure and start the backend server.

    Args:
        back_functions: List of (setup_webserver_function, config) tuples for extensions
        bot: Optional existing bot instance. When omitted, a new bot is created via
            :func:`src.startup.bot.create_bot`.

    """
    from src.startup.bot import create_bot  # noqa: PLC0415

    app = create_backend_app()
    if bot is None:
        bot = create_bot(config.bot)
    setup_backend_extensions(app, bot, back_functions)
    await run_backend_only(app, bot, config.bot.token, config.backend)


__all__ = [
    "create_backend_app",
    "create_backend_bot",
    "run_backend_only",
    "run_startup_functions",
    "serve_backend",
    "setup_and_start_backend",
    "setup_backend_extensions",
    "start_backend",
]

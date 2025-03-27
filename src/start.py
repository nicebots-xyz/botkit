# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import asyncio
import importlib
import importlib.util
from glob import iglob
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import discord
import yaml
from discord.errors import LoginFailure
from discord.ext import commands
from quart import Quart

from src import custom, i18n
from src.config import config
from src.config.models import BotConfig, Extension, RestConfig
from src.i18n.classes import ExtensionTranslation
from src.log import logger, patch
from src.utils import setup_func, unzip_extensions, validate_module

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine
    from types import ModuleType

    FunctionlistType = list[tuple[Callable[..., Any], Extension]]


async def start_bot(bot: custom.Bot, token: str, rest_config: RestConfig, public_key: str | None = None) -> None:
    try:
        if isinstance(bot, custom.CustomRestBot):
            if not public_key:
                raise TypeError("CustomRestBot requires a public key to start.")  # noqa: TRY301
            await bot.start(
                token=token,
                public_key=public_key,
                health=rest_config.health,
                uvicorn_options={
                    "host": rest_config.host,
                    "port": rest_config.port,
                },
            )
        else:
            await bot.start(token)
    except LoginFailure as e:
        logger.critical("Failed to log in, is the bot token valid?")
        logger.debug("", exc_info=e)
    except Exception as e:  # noqa: BLE001
        logger.critical("An unexpected error occurred while starting the bot.")
        logger.debug("", exc_info=e)


async def start_backend(app: Quart, bot: discord.Bot, token: str) -> None:
    from hypercorn.asyncio import serve  # pyright: ignore [reportUnknownVariableType]
    from hypercorn.config import Config
    from hypercorn.logging import Logger as HypercornLogger

    class CustomLogger(HypercornLogger):
        def __init__(
            self,
            *args,  # pyright: ignore [reportUnknownParameterType,reportMissingParameterType]  # noqa: ANN002
            **kwargs,  # pyright: ignore [reportUnknownParameterType,reportMissingParameterType]  # noqa: ANN003
        ) -> None:
            super().__init__(
                *args,  # pyright: ignore [reportUnknownArgumentType]
                **kwargs,
            )
            if self.error_logger:
                patch(self.error_logger)
            if self.access_logger:
                patch(self.access_logger)

    app_config = Config()
    app_config.accesslog = "-"
    app_config.logger_class = CustomLogger
    app_config.include_server_header = False  # security
    app_config.bind = ["0.0.0.0:5000"]
    try:
        await bot.login(token)
        await serve(app, app_config)
        patch("hypercorn.error")
    except Exception as e:  # noqa: BLE001
        logger.critical("An error occurred while starting the backend server.")
        logger.debug("", exc_info=e)


def load_extensions() -> tuple[
    "FunctionlistType",
    "FunctionlistType",
    "FunctionlistType",
    "list[ExtensionTranslation]",
]:
    """Load extensions from the extensions directory.

    Returns:
        tuple[FunctionlistType, FunctionlistType, FunctionlistType, list[ExtensionTranslation]]: A tuple containing
        the bot functions, backend functions, startup functions, and translations.

    """
    bot_functions: FunctionlistType = []
    back_functions: FunctionlistType = []
    startup_functions: FunctionlistType = []
    translations: list[ExtensionTranslation] = []
    for _extension in iglob("src/extensions/*"):
        extension = Path(_extension)
        name = extension.name
        if name.endswith(("_", "_/", ".py")):
            continue

        _, its_config = config.get_extension(name, {})
        if its_config and not its_config.get("enabled"):
            # Early return if extension is configured to be disabled explicitly
            continue

        try:
            module: ModuleType = importlib.import_module(f"src.extensions.{name}")
        except ImportError as e:
            logger.error(f"Failed to import extension {name}")
            logger.debug("", exc_info=e)
            continue

        its_config = its_config or cast("Extension", module.default)
        if not its_config.get("enabled"):
            del module
            continue

        logger.info(f"Loading extension {name}")
        translation: ExtensionTranslation | None = None
        if (translation_path := (extension / "translations.yml")).exists():
            try:
                translation = i18n.load_translation(str(translation_path))
                translations.append(translation)
            except yaml.YAMLError as e:
                logger.error(f"Error loading translation {translation_path}: {e}")
        else:
            logger.warning(f"No translation found for extension {name}")

        validate_module(module, its_config)
        if translation and translation.strings:
            its_config["translations"] = translation.strings
        if hasattr(module, "setup") and callable(module.setup):
            bot_functions.append((module.setup, its_config))
        if hasattr(module, "setup_webserver") and callable(module.setup_webserver):
            back_functions.append((module.setup_webserver, its_config))
        if hasattr(module, "on_startup") and callable(module.on_startup):
            startup_functions.append((module.on_startup, its_config))

    return bot_functions, back_functions, startup_functions, translations


async def setup_and_start_bot(
    bot_functions: "FunctionlistType",
    translations: list[ExtensionTranslation],
    config: BotConfig,
) -> None:
    intents = discord.Intents.default()
    if config.prefix:
        intents.message_content = True
    cls = custom.CustomRestBot if config.rest else custom.CustomBot
    bot = cls(
        intents=intents,
        help_command=None,
        command_prefix=(str(config.prefix) or commands.when_mentioned),
        cache_type=config.cache.type,
        cache_config=config.cache.redis,
    )
    for function, its_config in bot_functions:
        setup_func(function, bot=bot, config=its_config)
    i18n.apply(bot, translations)
    if not config.prefix:
        bot.prefixed_commands = {}
    if not config.slash:
        bot._pending_application_commands = []  # pyright: ignore[reportPrivateUsage]
    await start_bot(bot, config.token, config.rest, config.public_key)


async def setup_and_start_backend(
    back_functions: "FunctionlistType",
) -> None:
    back_bot = discord.Bot(intents=discord.Intents.default())
    app = Quart("backend")
    for function, its_config in back_functions:
        setup_func(function, app=app, bot=back_bot, config=its_config)
    await start_backend(app, back_bot, config.bot.token)


async def run_startup_functions(
    startup_functions: "FunctionlistType",
    app: Quart | None,
    back_bot: discord.Bot | None,
) -> None:
    startup_coros = [
        setup_func(function, app=app, bot=back_bot, config=its_config) for function, its_config in startup_functions
    ]
    await asyncio.gather(*startup_coros)


async def start(run_bot: bool | None = None, run_backend: bool | None = None) -> None:
    if not config.bot.token:
        logger.critical("No bot token provided in config, exiting...")
        return
    if config.db.enabled:
        from src.database.config import init

        logger.info("Initializing database...")
        await init()

    unzip_extensions()
    run_bot = run_bot if run_bot is not None else config.use.bot
    run_backend = run_backend if run_backend is not None else config.use.backend

    bot_functions, back_functions, startup_functions, translations = load_extensions()

    coros: list[Coroutine[Any, Any, Any]] = []
    if bot_functions and run_bot:
        coros.append(setup_and_start_bot(bot_functions, translations, config.bot))
    if back_functions and run_backend:
        coros.append(setup_and_start_backend(back_functions))
    if not coros:
        logger.error("Nothing to start, exiting...")
        return

    if startup_functions:
        app = Quart("backend") if (back_functions and run_backend) else None
        back_bot = discord.Bot(intents=discord.Intents.default()) if (back_functions and run_backend) else None
        await run_startup_functions(startup_functions, app, back_bot)

    await asyncio.gather(*coros)

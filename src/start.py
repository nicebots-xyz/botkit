# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import asyncio
import importlib
import importlib.util
from glob import iglob
from os.path import basename, splitext
from typing import TYPE_CHECKING, Any, TypedDict

import discord
import yaml
from discord.errors import LoginFailure
from discord.ext import commands
from quart import Quart

from src import custom, i18n
from src.config import config
from src.i18n.classes import ExtensionTranslation
from src.log import logger, patch
from src.utils import setup_func, unzip_extensions, validate_module
from src.utils.iterator import next_default

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine
    from types import ModuleType

    class FunctionConfig(TypedDict):
        enabled: bool

    FunctionlistType = list[tuple[Callable[..., Any], FunctionConfig]]


async def start_bot(bot: custom.Bot, token: str) -> None:
    try:
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


def load_extensions() -> (
    tuple[
        "FunctionlistType",
        "FunctionlistType",
        "FunctionlistType",
        "list[ExtensionTranslation]",
    ]
):
    """Load extensions from the extensions directory.

    Returns:
        tuple[FunctionlistType, FunctionlistType, FunctionlistType, list[ExtensionTranslation]]: A tuple containing
        the bot functions, backend functions, startup functions, and translations.

    """
    bot_functions: FunctionlistType = []
    back_functions: FunctionlistType = []
    startup_functions: FunctionlistType = []
    translations: list[ExtensionTranslation] = []
    for extension in iglob("src/extensions/*"):
        name = splitext(basename(extension))[0]
        if name.endswith(("_", "_/", ".py")):
            continue

        its_config = config["extensions"].get(name, config["extensions"].get(name.replace("_", "-"), {}))
        try:
            module: ModuleType = importlib.import_module(f"src.extensions.{name}")
        except ImportError as e:
            logger.error(f"Failed to import extension {name}")
            logger.debug("", exc_info=e)
            continue
        if not its_config:
            its_config = module.default
            config["extensions"][name] = its_config
        if not its_config["enabled"]:
            del module
            continue
        logger.info(f"Loading extension {name}")
        translation: ExtensionTranslation | None = None
        if translation_path := next_default(iglob(extension + "/translations.yml")):
            try:
                translation = i18n.load_translation(translation_path)
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
    config: dict[str, Any],
) -> None:
    intents = discord.Intents.default()
    if config.get("prefix"):
        intents.message_content = True
    # Get cache configuration
    cache_config = config.get("cache", {})
    bot = custom.Bot(
        intents=intents,
        help_command=None,
        command_prefix=(config.get("prefix", {}).get("prefix") or commands.when_mentioned),
        cache_type=cache_config.get("type", "memory"),
        cache_config=cache_config.get("redis"),
    )
    for function, its_config in bot_functions:
        setup_func(function, bot=bot, config=its_config)
    i18n.apply(bot, translations)
    if not config.get("prefix", {}).get("enabled", True):
        bot.prefixed_commands = {}
    if not config.get("slash", {}).get("enabled", True):
        bot._pending_application_commands = []  # pyright: ignore[reportPrivateUsage]  # noqa: SLF001
    await start_bot(bot, config["token"])


async def setup_and_start_backend(
    back_functions: "FunctionlistType",
) -> None:
    back_bot = discord.Bot(intents=discord.Intents.default())
    app = Quart("backend")
    for function, its_config in back_functions:
        setup_func(function, app=app, bot=back_bot, config=its_config)
    await start_backend(app, back_bot, config["bot"]["token"])


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
    if not config.get("bot", {}).get("token"):
        logger.critical("No bot token provided in config, exiting...")
        return
    if config.get("db", {}).get("enabled", False):
        from src.database.config import init

        logger.info("Initializing database...")
        await init()

    unzip_extensions()
    run_bot = run_bot if run_bot is not None else config.get("use", {}).get("bot", True)
    run_backend = run_backend if run_backend is not None else config.get("use", {}).get("backend", True)

    bot_functions, back_functions, startup_functions, translations = load_extensions()

    coros: list[Coroutine[Any, Any, Any]] = []
    if bot_functions and run_bot:
        coros.append(setup_and_start_bot(bot_functions, translations, config.get("bot", {})))
    if back_functions and run_backend:
        coros.append(setup_and_start_backend(back_functions))
    if not coros:
        logger.error("No extensions to run, exiting...")
        return

    if startup_functions:
        app = Quart("backend") if (back_functions and run_backend) else None
        back_bot = discord.Bot(intents=discord.Intents.default()) if (back_functions and run_backend) else None
        await run_startup_functions(startup_functions, app, back_bot)

    await asyncio.gather(*coros)

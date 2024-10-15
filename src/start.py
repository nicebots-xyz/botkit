import discord
import importlib
import importlib.util
import asyncio

import yaml
from quart import Quart
from glob import iglob
from src.i18n.classes import ExtensionTranslation
from src.config import config, store_config
from src.log import logger, patch
from os.path import splitext, basename
from types import ModuleType
from typing import Any, Callable, TypedDict, TYPE_CHECKING
from collections.abc import Coroutine
from src.utils import validate_module, unzip_extensions, setup_func
from src import i18n
from src.utils.iterator import next_default
from src import custom

if TYPE_CHECKING:
    FunctionConfig = TypedDict("FunctionConfig", {"enabled": bool})
    FunctionlistType = list[tuple[Callable[..., Any], FunctionConfig]]


async def start_bot(bot: discord.Bot, token: str):
    await bot.start(token)


async def start_backend(app: Quart, bot: discord.Bot, token: str):
    from hypercorn.config import Config
    from hypercorn.logging import Logger as HypercornLogger
    from hypercorn.asyncio import serve  # pyright: ignore [reportUnknownVariableType]

    class CustomLogger(HypercornLogger):
        def __init__(
            self,
            *args,  # pyright: ignore [reportUnknownParameterType,reportMissingParameterType]
            **kwargs,  # pyright: ignore [reportUnknownParameterType,reportMissingParameterType]
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
    await bot.login(token)
    await serve(app, app_config)
    patch("hypercorn.error")


def load_extensions() -> (
    tuple[
        "FunctionlistType",
        "FunctionlistType",
        "FunctionlistType",
        "list[ExtensionTranslation]",
    ]
):
    bot_functions: "FunctionlistType" = []
    back_functions: "FunctionlistType" = []
    startup_functions: "FunctionlistType" = []
    translations: list[ExtensionTranslation] = []
    for extension in iglob("src/extensions/*"):
        translation: ExtensionTranslation | None = None
        if translation_path := next_default(iglob(extension + "/translations.yml")):
            try:
                translation = i18n.load_translation(translation_path)
                translations.append(translation)
            except yaml.YAMLError as e:
                logger.error(f"Error loading translation {translation_path}: {e}")
        else:
            logger.warning(f"No translation found for extension {extension}")
        name = splitext(basename(extension))[0]
        its_config = config["extensions"].get(name, {})
        logger.info(f"Loading extension {name}")
        module: ModuleType = importlib.import_module(f"src.extensions.{name}")
        if not its_config:
            its_config = module.default
            config["extensions"][name] = its_config
        if not its_config["enabled"]:
            del module
            continue

        validate_module(module, its_config)
        if translation and translation.strings:
            its_config["translation"] = translation.strings
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
):
    bot = custom.Bot(intents=discord.Intents.default())
    for function, its_config in bot_functions:
        setup_func(function, bot=bot, config=its_config)
    i18n.apply(bot, translations)
    await start_bot(bot, config["bot"]["token"])


async def setup_and_start_backend(
    back_functions: "FunctionlistType",
):
    back_bot = discord.Bot(intents=discord.Intents.default())
    app = Quart("backend")
    for function, its_config in back_functions:
        setup_func(function, app=app, bot=back_bot, config=its_config)
    await start_backend(app, back_bot, config["bot"]["token"])


async def run_startup_functions(
    startup_functions: "FunctionlistType",
    app: Quart | None,
    back_bot: discord.Bot | None,
):
    startup_coros = [
        setup_func(function, app=app, bot=back_bot, config=its_config)
        for function, its_config in startup_functions
    ]
    await asyncio.gather(*startup_coros)


async def main(run_bot: bool = True, run_backend: bool = True):
    assert config.get("bot", {}).get("token"), "No bot token provided in config"
    unzip_extensions()

    bot_functions, back_functions, startup_functions, translations = load_extensions()

    coros: list[Coroutine[Any, Any, Any]] = []
    if bot_functions and run_bot:
        coros.append(setup_and_start_bot(bot_functions, translations))
    if back_functions and run_backend:
        coros.append(setup_and_start_backend(back_functions))
    assert coros, "No extensions to run"

    if startup_functions:
        app = Quart("backend") if (back_functions and run_backend) else None
        back_bot = (
            discord.Bot(intents=discord.Intents.default())
            if (back_functions and run_backend)
            else None
        )
        await run_startup_functions(startup_functions, app, back_bot)

    await asyncio.gather(*coros)

    store_config()

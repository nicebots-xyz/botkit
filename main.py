import discord
import importlib
import importlib.util
import asyncio

from inspect import signature
from quart import Quart
from glob import iglob
from src.config import config, store_config
from src.logging import logger, patch
from os.path import splitext, basename
from types import ModuleType
from typing import Any, Coroutine, Callable
from src.utils import validate_module, unzip_extensions


# noinspection PyUnusedLocal
async def start_bot(bot: discord.Bot, token: str):
    await bot.start(config["bot"]["token"])


async def start_backend(app: Quart, bot: discord.Bot, token: str):
    from hypercorn.config import Config
    from hypercorn.logging import Logger as HypercornLogger
    from hypercorn.asyncio import serve

    class CustomLogger(HypercornLogger):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
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


def setup_func(func: callable, **kwargs) -> Any:
    parameters = signature(func).parameters
    func_kwargs = {}
    for name, parameter in parameters.items():
        if name in kwargs:
            func_kwargs[name] = kwargs[name]
        elif parameter.default != parameter.empty:
            func_kwargs[name] = parameter.default
        else:
            raise TypeError(f"Missing required argument {name}")
    return func(**func_kwargs)


async def main():
    assert (config.get("bot", {}) or {}).get(
        "token"
    ), f"No bit token provided in config"
    unzip_extensions()

    bot_functions: list[tuple[Callable, dict[Any]]] = []
    back_functions: list[tuple[Callable, dict[Any]]] = []
    startup_functions: list[tuple[Callable, dict[Any]]] = []

    for extension in iglob("src/extensions/*"):
        name = splitext(basename(extension))[0]
        its_config = config["extensions"].get(name, {})
        logger.info(f"Loading extension {name}")
        module: ModuleType = importlib.import_module(f"src.extensions.{name}")
        if not its_config:
            # use default config if not present
            its_config = module.default
            config["extensions"][name] = its_config
        if not its_config["enabled"]:
            del module
            continue

        validate_module(module, its_config)

        if hasattr(module, "setup") and callable(module.setup):
            bot_functions.append((module.setup, its_config))
        if hasattr(module, "setup_webserver") and callable(module.setup_webserver):
            back_functions.append((module.setup_webserver, its_config))
        if hasattr(module, "on_startup") and callable(module.on_startup):
            startup_functions.append((module.on_startup, its_config))

    startup_coros: list[Coroutine] = []
    coros: list[Coroutine] = []

    bot = None
    back_bot = None
    app = None

    if bot_functions:
        bot = discord.Bot(intents=discord.Intents.default())
        for function, its_config in bot_functions:
            setup_func(function, bot=bot, config=its_config)
        coros.append(start_bot(bot, config["bot"]["token"]))

    if back_functions:
        back_bot = discord.Bot(intents=discord.Intents.default())
        app = Quart("backend")
        for function, its_config in back_functions:
            setup_func(function, app=app, bot=back_bot, config=its_config)
        coros.append(start_backend(app, back_bot, config["bot"]["token"]))
    assert coros, "No extensions to run"

    if startup_functions:
        for function, its_config in startup_functions:
            startup_coros.append(
                setup_func(function, app=app, bot=back_bot, config=its_config)
            )

    await asyncio.gather(*startup_coros)
    await asyncio.gather(*coros)

    store_config()


if __name__ == "__main__":
    asyncio.run(main())

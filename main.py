import discord
import importlib
import importlib.util
import asyncio

from flask import Flask
from glob import iglob
from src.config import config, store_config
from src.logging import logger
from os.path import splitext, basename
from types import ModuleType
from typing import Any, Coroutine
from src.utils import validate_module, unzip_extensions


# noinspection PyUnusedLocal
async def start_bot(bot: discord.Bot, token: str):
    await bot.start(config["bot"]["token"])


async def start_backend(app: Flask, bot: discord.Bot, token: str):
    from hypercorn.config import Config
    from hypercorn.asyncio import serve

    app.logger.handlers = logger.handlers

    await bot.login(token)
    app_config = Config()
    app_config.include_server_header = False  # security
    app_config.bind = ["0.0.0.0:5000"]
    await serve(app, app_config)


async def main():
    assert (config.get("bot", {}) or {}).get("token"), f"No token provided in config"
    unzip_extensions()
    bot_modules: list[tuple[ModuleType, dict[Any]]] = []
    back_modules: list[tuple[ModuleType, dict[Any]]] = []
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
            bot_modules.append((module, its_config))
        if hasattr(module, "setup_webserver") and callable(module.setup_webserver):
            back_modules.append((module, its_config))

    coros: list[Coroutine] = []

    if bot_modules:
        bot = discord.Bot(intents=discord.Intents.default())
        for module, its_config in bot_modules:
            module.setup(bot=bot, config=its_config)
        coros.append(start_bot(bot, config["bot"]["token"]))

    if back_modules:
        back_bot = discord.Bot(intents=discord.Intents.default())
        app = Flask("backend")
        for module, its_config in back_modules:
            module.setup_webserver(app=app, bot=back_bot, config=its_config)

        coros.append(start_backend(app, back_bot, config["bot"]["token"]))
    assert coros, "No modules to run"
    await asyncio.gather(*coros)

    store_config()


if __name__ == "__main__":
    asyncio.run(main())

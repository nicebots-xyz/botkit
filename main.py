import discord
import importlib
import importlib.util

from src.config import config
from src.logging import get_logger


def check_module(module_name: str) -> bool:
    spec = importlib.util.find_spec(module_name)
    return spec is not None


def main():
    bot = discord.Bot(intents=discord.Intents.default())

    logger = get_logger(name="Main")
    logger.info("Starting bot")

    for extension, its_config in config["extensions"].items():
        if its_config["enabled"]:
            if check_module(f"src.extensions.{extension}"):
                logger.info(f"Loading extension {extension}")
                module = importlib.import_module(f"src.extensions.{extension}")
                module.setup(bot, logger, its_config)
            elif check_module(extension):
                logger.info(f"Loading extension {extension}")
                module = importlib.import_module(extension)
                module.setup(bot, logger, its_config)
            else:
                logger.error(f"Extension {extension} not found")

    bot.run(config["bot"]["token"])

    logger.info("Bot stopped")


if __name__ == "__main__":
    main()

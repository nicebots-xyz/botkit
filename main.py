import discord
import importlib
import importlib.util

from glob import iglob
from src.config import config, store_config
from src.logging import logger
from os.path import splitext, basename
from types import ModuleType
from src.utils import validate_module, unzip_extensions


def main():
    bot = discord.Bot(intents=discord.Intents.default())
    # use iglob tgo iterate over all direct folders in src/extensions (no subfolders)
    unzip_extensions()
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
        validate_module(module)
        module.setup(bot=bot, config=its_config)

    store_config()

    bot.run(config["bot"]["token"])


if __name__ == "__main__":
    main()

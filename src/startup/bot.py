# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

"""Bot creation and initialization logic."""

from typing import Any

import discord
from discord.ext import commands

from src import custom, i18n
from src.config.models import BotConfig, RestConfig
from src.i18n.classes import ExtensionTranslation
from src.log import logger
from src.startup.types import SetupFunctionList
from src.utils import setup_func


def create_bot(config: BotConfig) -> custom.Bot:
    """Create a bot instance based on configuration.

    Args:
        config: Bot configuration including intents, prefix, and rest mode settings

    Returns:
        A configured CustomBot or CustomRestBot instance

    """
    intents = discord.Intents.default()
    if config.prefix:
        intents.message_content = True

    bot_class = custom.CustomRestBot if config.rest else custom.CustomBot

    return bot_class(
        intents=intents,
        help_command=None,
        command_prefix=(str(config.prefix) or commands.when_mentioned),
        cache_type=config.cache.type,
        cache_config=config.cache.redis,
        cache_app_emojis=config.cache_app_emojis,
    )


def setup_bot_extensions(
    bot: custom.Bot,
    bot_functions: SetupFunctionList,
    translations: list[ExtensionTranslation],
) -> None:
    """Set up all bot extensions and apply translations.

    Args:
        bot: The bot instance to configure
        bot_functions: List of (setup_function, config) tuples to execute
        translations: List of extension translations to apply

    """
    for function, its_config in bot_functions:
        setup_func(function, bot=bot, config=its_config)

    i18n.apply(bot, translations)


def configure_bot_features(bot: custom.Bot, config: BotConfig) -> None:
    """Configure bot features based on configuration.

    Disables prefixed commands or slash commands as specified in config.

    Args:
        bot: The bot instance to configure
        config: Bot configuration with feature flags

    """
    if not config.prefix:
        bot.prefixed_commands = {}

    if not config.slash:
        bot._pending_application_commands = []  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]


async def start_bot(bot: custom.Bot, token: str, rest_config: RestConfig, public_key: str | None = None) -> None:
    """Start the bot with appropriate configuration.

    Args:
        bot: The bot instance to start
        token: Discord bot token
        rest_config: REST API configuration (used if bot is CustomRestBot)
        public_key: Public key for REST bot authentication (required for CustomRestBot)

    Raises:
        TypeError: If CustomRestBot is used without a public key

    """
    try:
        if isinstance(bot, custom.CustomRestBot):
            if not public_key:
                raise TypeError("CustomRestBot requires a public key to start.")  # noqa: TRY301
            start_kwargs: dict[str, Any] = {
                "token": token,
                "public_key": public_key,
                "health": rest_config.health,
                "uvicorn_options": {
                    "host": rest_config.host,
                    "port": rest_config.port,
                },
            }
            await bot.start(**start_kwargs)
        else:
            await bot.start(token)
    except discord.LoginFailure as e:
        logger.critical("Failed to log in, is the bot token valid?")
        logger.debug("", exc_info=e)
    except Exception as e:  # noqa: BLE001
        logger.critical("An unexpected error occurred while starting the bot.")
        logger.debug("", exc_info=e)


async def setup_and_start_bot(
    bot_functions: SetupFunctionList,
    translations: list[ExtensionTranslation],
    config: BotConfig,
) -> None:
    """Create, configure, and start the bot.

    This is a convenience function that combines bot creation, extension setup,
    feature configuration, and bot startup.

    Args:
        bot_functions: List of (setup_function, config) tuples for extensions
        translations: List of extension translations
        config: Bot configuration

    """
    bot = create_bot(config)
    setup_bot_extensions(bot, bot_functions, translations)
    configure_bot_features(bot, config)
    await start_bot(bot, config.token, config.rest, config.public_key)


__all__ = [
    "configure_bot_features",
    "create_bot",
    "setup_and_start_bot",
    "setup_bot_extensions",
    "start_bot",
]

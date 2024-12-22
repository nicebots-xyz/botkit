# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

from logging import getLogger
from typing import TYPE_CHECKING, Any, override

import aiocache
import discord
from discord import Message
from discord.ext import bridge
from discord.ext.bridge import (
    BridgeExtContext,
)

from src.i18n.classes import ExtensionTranslation, TranslationWrapper, apply_locale

logger = getLogger("bot")


class ApplicationContext(bridge.BridgeApplicationContext):
    def __init__(self, bot: "Bot", interaction: discord.Interaction) -> None:
        self.translations: TranslationWrapper = TranslationWrapper({}, "en-US")  # empty placeholder
        super().__init__(bot=bot, interaction=interaction)
        self.bot: Bot

    @override
    def __setattr__(self, key: Any, value: Any) -> None:
        if key == "command" and hasattr(value, "translations"):
            self.translations = apply_locale(
                value.translations,
                self.locale,
            )
        super().__setattr__(key, value)


class ExtContext(bridge.BridgeExtContext):
    def __init__(self, **kwargs: Any) -> None:
        self.translations: TranslationWrapper = TranslationWrapper({}, "en-US")  # empty placeholder
        super().__init__(**kwargs)
        self.bot: Bot

    def load_translations(self) -> None:
        if hasattr(self.command, "translations") and self.command.translations:  # pyright: ignore[reportUnknownArgumentType,reportOptionalMemberAccess,reportAttributeAccessIssue]
            locale: str | None = None
            if guild := self.guild:
                locale = guild.preferred_locale
            self.translations = apply_locale(
                self.command.translations,
                locale,
            )


class Bot(bridge.Bot):
    def __init__(
        self, *args: Any, cache_type: str = "memory", cache_config: dict[str, Any] | None = None, **options: Any
    ) -> None:
        self.translations: list[ExtensionTranslation] = options.pop("translations", [])

        self.botkit_cache: aiocache.BaseCache
        # Initialize cache based on type and config
        if cache_type == "redis":
            if cache_config:
                logger.info("Using Redis cache")
                self.botkit_cache = aiocache.RedisCache(
                    endpoint=cache_config.get("host", "localhost"),
                    port=cache_config.get("port", 6379),
                    db=cache_config.get("db", 0),
                    password=cache_config.get("password"),
                    ssl=cache_config.get("ssl", False),
                    namespace="botkit",
                )
            else:
                logger.warning(
                    "Redis cache type specified but no configuration provided. Falling back to memory cache."
                )
                self.botkit_cache = aiocache.SimpleMemoryCache(namespace="botkit")
        else:
            logger.info("Using memory cache")
            self.botkit_cache = aiocache.SimpleMemoryCache(namespace="botkit")

        super().__init__(*args, **options)

        @self.listen(name="on_ready", once=True)
        async def on_ready() -> None:  # pyright: ignore[reportUnusedFunction]
            logger.success("Bot started successfully")  # pyright: ignore[reportAttributeAccessIssue]

    @override
    async def get_application_context(
        self,
        interaction: discord.Interaction,
        cls: None | type[bridge.BridgeApplicationContext] = None,
    ) -> bridge.BridgeApplicationContext:
        cls = cls if cls is not None else ApplicationContext
        return await super().get_application_context(interaction, cls=cls)

    @override
    async def get_context(
        self,
        message: Message,
        cls: None | type[bridge.BridgeExtContext] = None,
    ) -> BridgeExtContext:
        cls = cls if cls is not None else ExtContext
        ctx = await super().get_context(message, cls=cls)
        if isinstance(ctx, ExtContext):
            ctx.load_translations()
        return ctx


Context: ApplicationContext = ApplicationContext  # pyright: ignore [reportRedeclaration]

if TYPE_CHECKING:  # temp fix for https://github.com/Pycord-Development/pycord/pull/2611
    type Context = ExtContext | ApplicationContext
    ...  # for some reason, this makes pycharm happy

__all__ = ["ApplicationContext", "Bot", "Context", "ExtContext"]

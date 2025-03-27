# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import contextlib
from logging import getLogger
from typing import TYPE_CHECKING, Any, override

import aiocache
import discord
import pycord_rest
import uvicorn
from discord import Interaction, Message, WebhookMessage
from discord.ext import bridge
from discord.ext.bridge import (
    BridgeExtContext,
)

from src import log
from src.config.models import RedisConfig
from src.i18n.classes import ExtensionTranslation, RawTranslation, TranslationWrapper, apply_locale

if TYPE_CHECKING:
    from src.database.models import Guild, User

logger = getLogger("bot")


class ApplicationContext(bridge.BridgeApplicationContext):
    def __init__(self, bot: "Bot", interaction: discord.Interaction) -> None:
        self.translations: TranslationWrapper[dict[str, RawTranslation]] = TranslationWrapper(
            {}, "en-US"
        )  # empty placeholder
        super().__init__(bot=bot, interaction=interaction)
        self.bot: Bot
        self.user_obj: User | None = None
        self.guild_obj: Guild | None = None
        self.custom_attrs: dict[str, Any] = {}

    @override
    def __setattr__(self, key: Any, value: Any) -> None:
        if key == "command" and hasattr(value, "translations"):
            self.translations = apply_locale(
                value.translations,
                self.locale,
            )
        super().__setattr__(key, value)


async def remove_reaction(user: discord.User, message: discord.Message, emoji: str) -> None:
    await message.remove_reaction(emoji, user)


class ExtContext(bridge.BridgeExtContext):
    def __init__(self, **kwargs: Any) -> None:
        self.translations: TranslationWrapper = TranslationWrapper({}, "en-US")  # empty placeholder
        super().__init__(**kwargs)
        self.bot: Bot
        self.user_obj: User | None = None
        self.guild_obj: Guild | None = None
        self.custom_attrs: dict[str, Any] = {}

    def load_translations(self) -> None:
        if hasattr(self.command, "translations") and self.command.translations:  # pyright: ignore[reportUnknownArgumentType,reportOptionalMemberAccess,reportAttributeAccessIssue]
            locale: str | None = None
            if guild := self.guild:
                locale = guild.preferred_locale
            self.translations = apply_locale(
                self.command.translations,  # pyright: ignore [reportAttributeAccessIssue, reportOptionalMemberAccess, reportUnknownArgumentType]
                locale,
            )

    @override
    async def defer(self, *args: Any, **kwargs: Any) -> None:
        await super().defer(*args, **kwargs)
        with contextlib.suppress(Exception):
            await self.message.add_reaction("🔄")

    @override
    async def respond(self, *args: Any, **kwargs: Any) -> "Interaction | WebhookMessage | Message":
        r = await super().respond(*args, **kwargs)
        with contextlib.suppress(Exception):
            if self.me:
                await remove_reaction(self.me, self.message, "🔄")
        return r


class CustomBot(bridge.Bot):
    __rest__: bool = False

    def __init__(
        self, *args: Any, cache_type: str = "memory", cache_config: RedisConfig | None = None, **options: Any
    ) -> None:
        self.translations: list[ExtensionTranslation] = options.pop("translations", [])

        self.botkit_cache: aiocache.BaseCache
        # Initialize cache based on type and config
        if cache_type == "redis":
            if cache_config:
                logger.info("Using Redis cache")
                self.botkit_cache = aiocache.RedisCache(
                    endpoint=cache_config.host,
                    port=cache_config.port,
                    db=cache_config.db,
                    password=cache_config.password,
                    ssl=cache_config.ssl,
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

    @property
    @override
    def intents(self) -> discord.Intents:
        """The intents configured for this connection or a copy of the intents if the bot is connected.

        Returns
        -------
        :class:`Intents`
            The intents configured for this Client.

        """
        # _connection._intents returns the intents themselves, _connection.intents returns a copy
        # so if the bot is connected, we return a copy so that changes don't affect the connection
        # if the bot is not connected, we return the actual intents so that the user can make changes
        if self.ws is None:  # pyright: ignore [reportUnnecessaryComparison]
            return self._connection._intents  # noqa: SLF001  # pyright: ignore [reportPrivateUsage]
        return self._connection.intents

    @intents.setter
    def intents(self, value: Any) -> None:  # pyright: ignore [reportExplicitAny]
        """Set the intents for this Client.

        Parameters
        ----------
        value: :class:`Intents`
            The intents to set for this Client.

        Raises
        ------
        TypeError
            The value is not an instance of Intents.
        AttributeError
            The intents cannot be changed after the connection is established.

        """
        if not isinstance(value, discord.Intents):
            raise TypeError(f"Intents must be an instance of Intents not {value.__class__!r}")
        if self.ws is not None:  # pyright: ignore [reportUnnecessaryComparison]
            raise AttributeError("Cannot change intents after the connection is established.")
        self._connection._intents.value = value.value  # noqa: SLF001  # pyright: ignore [reportPrivateUsage]


class CustomUvicornConfig(uvicorn.Config):
    @override
    def configure_logging(self) -> None:
        super().configure_logging()
        log.patch("uvicorn")
        log.patch("uvicorn.asgi")
        log.patch("uvicorn.error")
        log.patch("uvicorn.access")


class CustomRestBot(pycord_rest.Bot, CustomBot):  # pyright: ignore[reportIncompatibleMethodOverride,reportUnsafeMultipleInheritance]
    __rest__: bool = True

    _UvicornConfig: type[uvicorn.Config] = CustomUvicornConfig

    def __init__(
        self, *args: Any, cache_type: str = "memory", cache_config: RedisConfig | None = None, **options: Any
    ) -> None:
        CustomBot.__init__(self, *args, cache_type=cache_type, cache_config=cache_config, **options)
        pycord_rest.Bot.__init__(self, *args, **options)

        @self.listen(name="on_connect", once=True)
        async def on_connect() -> None:
            logger.success("Rest Bot connected successfully")  # pyright: ignore[reportAttributeAccessIssue]


type Bot = CustomBot | CustomRestBot

if not TYPE_CHECKING:
    Context: ApplicationContext = ApplicationContext

if TYPE_CHECKING:  # temp fix for https://github.com/Pycord-Development/pycord/pull/2611
    type Context = ExtContext | ApplicationContext
    ...  # for some reason, this makes pycharm happy

__all__ = ["ApplicationContext", "Bot", "Context", "CustomBot", "CustomRestBot", "ExtContext"]

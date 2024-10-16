# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

from discord import Message
from discord.ext.bridge import BridgeExtContext  # pyright: ignore [reportMissingTypeStubs]
from typing_extensions import override
import discord
from src.i18n.classes import ExtensionTranslation, TranslationWrapper, apply_locale
from typing import Any, Union  # pyright: ignore[reportDeprecated]
from discord.ext import bridge


class ApplicationContext(bridge.BridgeApplicationContext):
    def __init__(self, bot: discord.Bot, interaction: discord.Interaction):
        self.translations: TranslationWrapper = TranslationWrapper(
            {}, "en-US"
        )  # empty placeholder
        super().__init__(bot=bot, interaction=interaction)  # pyright: ignore[reportUnknownMemberType]

    @override
    def __setattr__(self, key: Any, value: Any):
        if key == "command":
            if hasattr(value, "translations"):
                self.translations = apply_locale(
                    value.translations,
                    self.locale,
                )
        super().__setattr__(key, value)


class ExtContext(bridge.BridgeExtContext):
    def __init__(self, **kwargs: Any):
        self.translations: TranslationWrapper = TranslationWrapper(
            {}, "en-US"
        )  # empty placeholder
        super().__init__(**kwargs)  # pyright: ignore[reportUnknownMemberType]

    def load_translations(self):
        if hasattr(self.command, "translations") and self.command.translations:  # pyright: ignore[reportUnknownMemberType,reportUnknownArgumentType,reportOptionalMemberAccess,reportAttributeAccessIssue]
            locale: str | None = None
            if guild := self.guild:  # pyright: ignore[reportUnnecessaryComparison] # for some reason pyright thinks guild is function
                locale = guild.preferred_locale  # pyright: ignore[reportFunctionMemberAccess]
            self.translations = apply_locale(
                self.command.translations,  # pyright: ignore[reportUnknownMemberType,reportUnknownArgumentType,reportAttributeAccessIssue,reportOptionalMemberAccess]
                locale,
            )


class Bot(bridge.Bot):
    def __init__(self, *args: Any, **options: Any):
        self.translations: list[ExtensionTranslation] = options.pop("translations", [])
        super().__init__(*args, **options)  # pyright: ignore[reportUnknownMemberType]

    @override
    async def get_application_context(
        self,
        interaction: discord.Interaction,
        cls: None | type[bridge.BridgeApplicationContext] = None,
    ) -> bridge.BridgeApplicationContext:
        cls = cls if cls is not None else ApplicationContext
        return await super().get_application_context(interaction, cls=cls)  # pyright: ignore [reportUnknownMemberType]

    @override
    async def get_context(
        self,
        message: Message,
        cls: None | type[bridge.BridgeExtContext] = None,
    ) -> BridgeExtContext:
        cls = cls if cls is not None else ExtContext
        ctx = await super().get_context(message, cls=cls)  # pyright: ignore [reportUnknownMemberType]
        if isinstance(ctx, ExtContext):
            ctx.load_translations()
        return ctx


# if we used | we would sometimes need to use 'Context' instead of Context when type hinting bc else the interpreter will crash
Context = Union[ExtContext, ApplicationContext]  # pyright: ignore[reportDeprecated]

__all__ = ["Bot", "Context", "ExtContext", "ApplicationContext"]

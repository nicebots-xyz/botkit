# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

from typing import Any, final

import discord
from discord.ext import commands

from src import custom
from src.utils.cooldown import CooldownExceeded

from .handlers import error_handler
from .handlers.cooldown import CooldownErrorHandler
from .handlers.forbidden import ForbiddenErrorHandler
from .handlers.generic import GenericErrorHandler
from .handlers.not_found import NotFoundErrorHandler

default = {
    "enabled": True,
}


@final
class NiceErrors(commands.Cog):
    def __init__(self, bot: discord.Bot, sentry_sdk: bool, config: dict[str, Any]) -> None:
        self.bot = bot
        self.sentry_sdk = sentry_sdk
        self.config = config

    @discord.Cog.listener("on_application_command_error")
    async def on_error(
        self,
        ctx: custom.ApplicationContext,
        error: discord.ApplicationCommandInvokeError,
    ) -> None:
        await error_handler.handle_error(
            error,
            ctx,
            raw_translations=self.config["translations"],
            use_sentry_sdk=self.sentry_sdk,
        )

    @discord.Cog.listener("on_command_error")
    async def on_command_error(self, ctx: custom.ExtContext, error: commands.CommandError) -> None:
        await error_handler.handle_error(
            error,
            ctx,
            raw_translations=self.config["translations"],
            use_sentry_sdk=self.sentry_sdk,
        )

    @discord.Cog.listener("on_view_error")
    async def on_view_error(
        self,
        error: Exception,
        item: discord.ui.ViewItem[discord.ui.BaseView],  # noqa: ARG002
        interaction: discord.Interaction,
    ) -> None:
        await error_handler.handle_error(
            error,
            interaction,
            raw_translations=self.config["translations"],
            use_sentry_sdk=self.sentry_sdk,
        )

    def add_error_handler(self, *args: Any, **kwargs: Any) -> None:
        error_handler.add_error_handler(*args, **kwargs)


def setup(bot: custom.Bot, config: dict[str, Any]) -> None:
    bot.add_cog(NiceErrors(bot, bool(config.get("sentry", {}).get("dsn")), config))
    error_handler.add_error_handler(None, GenericErrorHandler(config["translations"]))
    error_handler.add_error_handler(commands.CommandNotFound, NotFoundErrorHandler(config["translations"]))
    error_handler.add_error_handler(discord.Forbidden, ForbiddenErrorHandler(config["translations"]))
    error_handler.add_error_handler(CooldownExceeded, CooldownErrorHandler(config["translations"]))

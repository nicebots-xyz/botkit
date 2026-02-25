# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

from typing import Any, Never, final

import discord
import sentry_sdk
from discord.ext import commands

from src import custom
from src.log import logger as base_logger
from src.utils.cooldown import CooldownExceeded

from .handlers import error_handler
from .handlers.cooldown import CooldownErrorHandler
from .handlers.forbidden import ForbiddenErrorHandler
from .handlers.generic import GenericErrorHandler
from .handlers.not_found import NotFoundErrorHandler

default = {
    "enabled": True,
}

logger = base_logger.getChild("nice_errors")


@final
class NiceErrors(commands.Cog):
    def __init__(self, bot: custom.Bot, sentry_sdk: bool, config: dict[str, Any]) -> None:
        self.bot = bot
        self.sentry_sdk = sentry_sdk
        self.config = config
        self.bot.on_error = self.on_error  # type: ignore[assignment]  # pyright: ignore[reportAttributeAccessIssue]
        super().__init__()

    async def on_error(
        self,
        event_name: str,  # noqa: ARG002
        *args: Never,  # noqa: ARG002
        exc: Exception,
        **kwargs: Never,  # noqa: ARG002
    ) -> None:
        if self.sentry_sdk:
            sentry_sdk.capture_exception(exc)
        logger.exception("Captured exception", exc_info=exc)

    @discord.Cog.listener("on_application_command_error")
    async def on_application_command_error(
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

# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import discord

from discord.ext import commands
from schema import Schema, Optional

from src import custom
from .handler import handle_error
from typing import Any

default = {
    "enabled": True,
}

schema = Schema(
    {
        "enabled": bool,
        Optional("sentry"): {"dsn": str},
    }
)


class NiceErrors(commands.Cog):
    def __init__(self, bot: discord.Bot, sentry_sdk: bool, config: dict[str, Any]):
        self.bot = bot
        self.sentry_sdk = sentry_sdk
        self.config = config

    @discord.Cog.listener("on_application_command_error")
    async def on_error(
        self,
        ctx: custom.ApplicationContext,
        error: discord.ApplicationCommandInvokeError,
    ):
        await handle_error(
            error,
            ctx,
            raw_translations=self.config["translations"],
            use_sentry_sdk=self.sentry_sdk,
        )

    @discord.Cog.listener("on_command_error")
    async def on_command_error(
        self, ctx: custom.ExtContext, error: commands.CommandError
    ):
        await handle_error(
            error,
            ctx,
            raw_translations=self.config["translations"],
            use_sentry_sdk=self.sentry_sdk,
        )


def setup(bot: custom.Bot, config: dict[str, Any]) -> None:
    bot.add_cog(NiceErrors(bot, bool(config.get("sentry", {}).get("dsn")), config))

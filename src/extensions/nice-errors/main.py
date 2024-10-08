import discord

from discord.ext import commands
from schema import Schema, Optional
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
    def __init__(self, bot: discord.Bot, sentry_sdk: bool):
        self.bot = bot
        self.sentry_sdk = sentry_sdk

    @discord.Cog.listener("on_application_command_error")
    async def on_error(
        self,
        ctx: discord.ApplicationContext,
        error: discord.ApplicationCommandInvokeError,
    ):
        await handle_error(error, ctx, self.sentry_sdk)

def setup(bot: discord.Bot, config: dict[str, Any]) -> None:
    bot.add_cog(NiceErrors(bot, bool(config.get("sentry", {}).get("dsn"))))

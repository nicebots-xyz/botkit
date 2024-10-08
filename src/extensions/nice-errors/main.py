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
    def __init__(self, bot: discord.Bot, sentry_sdk: Any | None):
        self.bot = bot
        self.sentry_sdk = sentry_sdk

    @discord.Cog.listener("on_application_command_error")
    async def on_error(
        self,
        ctx: discord.ApplicationContext,
        error: discord.ApplicationCommandInvokeError,
    ):
        await handle_error(error, ctx, self.sentry_sdk)

    @discord.slash_command()
    async def crashtest(self, ctx: discord.ApplicationContext, use_view: bool =True):
        if use_view:
            btn = discord.ui.Button(label="Kick me", style=discord.ButtonStyle.danger)
            async def callback(interaction):
                await interaction.user.kick(reason="AAA")
            btn.callback = callback
            view = discord.ui.View(btn)
            await ctx.respond("Click the button", view=view)
        else:
            await ctx.author.kick(reason="AAA")


def setup(bot: discord.Bot, config: dict[str, Any]) -> None:
    sentry_sdk = None
    if config.get("sentry", {}).get("dsn"):
        import sentry_sdk
    bot.add_cog(NiceErrors(bot, sentry_sdk))

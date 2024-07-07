import discord
import aiohttp

from quart import Quart
from discord.ext import commands
from schema import Schema
from src.logging import logger


default = {
    "enabled": True,
}

schema = Schema(
    {
        "enabled": bool,
    }
)


class NiceErrors(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.Cog.listener("on_application_command_error")
    async def on_error(
        self,
        ctx: discord.ApplicationContext,
        error: discord.ApplicationCommandInvokeError,
    ):
        if not isinstance(error.original, discord.Forbidden):
            await ctx.respond(
                "Whoops! An error occurred while executing this command", ephemeral=True
            )
            raise error
        await ctx.respond(
            f"Whoops! I don't have permission to do that\n`{error.args[0].split(':')[-1].strip()}`",
            ephemeral=True,
        )


def setup(bot: discord.Bot) -> None:
    bot.add_cog(NiceErrors(bot))

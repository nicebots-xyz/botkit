import logging
import discord

from discord.ext import commands, tasks
from typing import Optional, Callable


BASE_URL = "https://top.gg/api"

logger: logging.Logger
config: dict


class Ping(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="ping")
    async def ping(self, ctx: discord.ApplicationContext, ephemeral: bool = False):
        await ctx.respond(
            f"Pong! {round(self.bot.latency * 1000)}ms", ephemeral=ephemeral
        )


def setup(bot: discord.Bot, _logger: logging.Logger, _config: dict):
    global logger
    global config
    logger = _logger
    config = _config

    logger.info("Loading Ping extension")

    bot.add_cog(Ping(bot))

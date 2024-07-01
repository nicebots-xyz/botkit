import discord

from discord.ext import commands
from schema import Schema
from src.logging import logger


BASE_URL = "https://top.gg/api"

default = {
    "enabled": True,
}

schema = Schema(
    {
        "enabled": bool,
    }
)


class Ping(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="ping")
    async def ping(
        self,
        ctx: discord.ApplicationContext,
        ephemeral: bool = False,
        embed: bool = False,
    ):
        await ctx.defer(ephemeral=ephemeral)
        if embed:
            embed = discord.Embed(
                title="Pong!",
                description=f"{round(self.bot.latency * 1000)}ms",
                color=discord.Colour.blurple(),
            )
            return await ctx.respond(embed=embed, ephemeral=ephemeral)
        return await ctx.respond(
            f"Pong! {round(self.bot.latency * 1000)}ms", ephemeral=ephemeral
        )


# noinspection PyUnusedLocal
def setup(bot: discord.Bot, config: dict):
    logger.info("Loading Ping extension")

    bot.add_cog(Ping(bot))

# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import discord
import aiohttp

from quart import Quart
from discord.ext import commands
from schema import Schema
from src.log import logger
from src import custom

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
        ctx: custom.ApplicationContext,
        ephemeral: bool = False,
        use_embed: bool = False,
    ):
        await ctx.defer(ephemeral=ephemeral)
        if use_embed:
            embed = discord.Embed(
                title="Pong!",
                description=ctx.translations.response.format(
                    latency=round(self.bot.latency * 1000)
                ),
                color=discord.Colour.blurple(),
            )
            return await ctx.respond(embed=embed, ephemeral=ephemeral)
        return await ctx.respond(
            f"Pong! {round(self.bot.latency * 1000)}ms", ephemeral=ephemeral
        )


def setup(bot: discord.Bot):
    bot.add_cog(Ping(bot))


def setup_webserver(app: Quart, bot: discord.Bot):
    @app.route("/ping")
    async def ping():
        bot_name = bot.user.name
        return {"message": f"{bot_name} is online"}


async def on_startup(config: dict):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://httpbin.org/user-agent") as resp:
            logger.info(f"HTTPBin user-agent: {await resp.text()}")
            logger.info(f"Ping extension config: {config}")

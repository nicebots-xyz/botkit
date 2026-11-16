# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

import aiohttp
import discord
from discord.ext import commands
from fastapi import FastAPI

from src import custom
from src.log import logger
from src.utils.cooldown import BucketType, cooldown

from .translation_types import PingCommandStrings

default = {
    "enabled": True,
}


class Ping(commands.Cog):
    def __init__(self, bot: custom.Bot) -> None:
        self.bot: custom.Bot = bot
        super().__init__()

    @discord.slash_command()
    @cooldown(
        key="ping",
        limit=1,
        per=5,
        strong=True,
        bucket_type=BucketType.USER,
    )
    async def ping(
        self,
        ctx: custom.ApplicationContext[PingCommandStrings],
        ephemeral: bool = False,
        use_embed: bool = False,
    ) -> None:
        await ctx.defer(ephemeral=ephemeral)
        if use_embed:
            embed = discord.Embed(
                title="Pong!",
                description=ctx.translations.response.format(latency=round(self.bot.latency * 1000)),
                color=discord.Colour.blurple(),
            )
            await ctx.respond(embed=embed, ephemeral=ephemeral)
            return
        await ctx.respond(f"Pong! {round(self.bot.latency * 1000)}ms", ephemeral=ephemeral)


def setup(bot: custom.Bot) -> None:
    bot.add_cog(Ping(bot))


def setup_webserver(app: FastAPI, bot: discord.Bot) -> None:
    @app.get("/ping")
    async def ping() -> dict[str, str]:  # pyright: ignore[reportUnusedFunction]
        if not bot.user:
            return {"message": "Bot is offline"}
        bot_name = bot.user.name
        return {"message": f"{bot_name} is online"}


async def on_startup(config: dict[str, bool]) -> None:
    async with aiohttp.ClientSession() as session, session.get("https://httpbin.org/user-agent") as resp:
        logger.info(f"HTTPBin user-agent: {await resp.text()}")
        logger.info(f"Ping extension config: {config}")

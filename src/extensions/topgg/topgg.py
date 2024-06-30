import logging

import discord
import aiohttp

from discord.ext import commands, tasks
from schema import Schema, And, Use, Optional
from src.logging import logger

BASE_URL = "https://top.gg/api"

default = {
    "token": "",
    "enabled": False,
}

schema = Schema(
    {
        "token": str,
        "enabled": bool,
    }
)


class Topgg(commands.Cog):
    def __init__(self, bot: discord.Bot, config: dict):
        self.bot = bot
        self.update_count_loop.start()

    def cog_unload(self) -> None:
        self.update_count_loop.cancel()

    @tasks.loop(minutes=30)
    async def update_count_loop(self):
        try:
            await self.update_count()
        except Exception as e:
            print(e)

    async def update_count(self):
        headers = {"Authorization": self.config["token"]}
        payload = {"server_count": len(self.bot.guilds)}
        url = f"{BASE_URL}/bots/{self.bot.user.id}/stats"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as resp:
                    # raise the eventual status code
                    resp.raise_for_status()
        # if 401 unauthorized
        except aiohttp.ClientResponseError as e:
            if e.status == 401:
                logger.error("Invalid Top.gg token")
        except Exception as e:
            logger.error(e)


def setup(bot: discord.Bot, config: dict):
    logger.info("Loading Top.gg extension")

    if not config.get("token"):
        logger.error("Top.gg token is not set up")
        return

    bot.add_cog(Topgg(bot))

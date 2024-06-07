import logging

import discord
import aiohttp

from discord.ext import commands, tasks
from typing import Optional, Callable


BASE_URL = "https://top.gg/api"

logger: logging.Logger
config: dict


class Topgg(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.update_count_loop.start()

    def cog_unload(self):
        self.update_count_loop.cancel()

    @tasks.loop(minutes=30)
    async def update_count_loop(self):
        try:
            await self.update_count()
        except Exception as e:
            print(e)

    async def update_count(self):
        headers = {"Authorization": config["token"]}
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


def setup(bot: discord.Bot, _logger: logging.Logger, _config: dict):
    global logger
    global config
    logger = _logger
    config = _config

    logger.info("Loading Top.gg extension")

    if not config.get("token"):
        logger.error("Top.gg token is not set up")
        return

    bot.add_cog(Topgg(bot))

import discord
import aiohttp

from discord.ext import commands
from schema import Schema
from src.logging import logger
from discord.ext import tasks


default = {
    "enabled": False,
    "url": "",
    "every": 60,
}

schema = Schema(
    {
        "enabled": bool,
        "url": str,
        "every": int,
    }
)


class Status(commands.Cog):
    def __init__(self, bot: discord.Bot, config: dict):
        self.bot = bot
        self.config = config
        tasks.loop(seconds=self.config["url"])(self.push_status_loop).start()

    @commands.Cog.listener(once=True)
    async def on_ready(self):
        self.push_status_loop.start()

    async def push_status_loop(self):
        try:
            await self.push_status()
            logger.info("Pushed status.")
        except Exception as e:
            logger.error(f"Failed to push status: {e}")

    async def push_status(self):
        ping = str(round(self.bot.latency * 1000))
        async with aiohttp.ClientSession() as session:
            async with session.get(self.config["url"] + ping) as resp:
                resp.raise_for_status()

def setup(bot: discord.Bot, config: dict):
    bot.add_cog(Status(bot, config))

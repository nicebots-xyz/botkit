import discord
import aiohttp

from discord.ext import commands, tasks
from schema import Schema, Optional
from src.log import logger

TOPGG_BASE_URL = "https://top.gg/api"
DISCORDSCOM_BASE_URL = "https://discords.com/bots/api/bot"

default = {
    "enabled": False,
}

schema = Schema(
    {
        Optional("topgg_token"): str,
        Optional("discordscom_token"): str,
        "enabled": bool,
    }
)


async def post_request(url: str, headers: dict, payload: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            # raise the eventual status code
            resp.raise_for_status()


async def try_post_request(url: str, headers: dict, payload: dict):
    try:
        await post_request(url, headers, payload)
    except aiohttp.ClientResponseError as e:
        if e.status == 401:
            logger.error("Invalid token")
        else:
            logger.error(e)
    except Exception as e:
        logger.error(e)


class Listings(commands.Cog):
    def __init__(self, bot: discord.Bot, config: dict):
        self.bot: discord.Bot = bot
        self.config: dict = config
        self.topgg = bool(config.get("topgg_token"))
        self.discordscom = bool(config.get("discordscom_token"))

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        self.update_count_loop.start()

    def cog_unload(self) -> None:
        self.update_count_loop.cancel()

    @tasks.loop(minutes=30)
    async def update_count_loop(self):
        try:
            if self.topgg:
                await self.update_count_topgg()
            if self.discordscom:
                await self.update_count_discordscom()
        except Exception as e:
            print(e)

    async def update_count_discordscom(self):
        headers = {
            "Authorization": self.config["discordscom_token"],
            "Content-Type": "application/json",
        }
        payload = {"server_count": len(self.bot.guilds)}
        url = f"{DISCORDSCOM_BASE_URL}/{self.bot.user.id}/setservers"
        await try_post_request(url, headers, payload)
        logger.info("Updated discords.com count")

    async def update_count_topgg(self):
        headers = {"Authorization": self.config["topgg_token"]}
        payload = {"server_count": len(self.bot.guilds)}
        url = f"{TOPGG_BASE_URL}/bots/{self.bot.user.id}/stats"
        await try_post_request(url, headers, payload)
        logger.info("Updated top.gg count")


def setup(bot: discord.Bot, config: dict):
    if not config.get("topgg_token") and not config.get("discordscom_token"):
        logger.error("Top.gg or Discords.com token not found")
        return

    bot.add_cog(Listings(bot, config))

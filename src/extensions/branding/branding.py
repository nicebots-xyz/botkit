import logging
import discord
import pytz
import random
from datetime import datetime

from typing_extensions import TypedDict
from discord.ext import commands, tasks


BASE_URL = "https://top.gg/api"

logger: logging.Logger
config: dict


class Footer(TypedDict):
    value: str | list[str] | None
    time: bool | None
    tz: str | None
    separator: str | None


class EmbedConfig(TypedDict):
    enabled: bool
    footer: Footer | None
    color: str | int | None
    author_url: str | None
    author: str | None


class StatusConfig(TypedDict):
    playing: list[str] | None
    watching: list[str] | None
    listening: list[str] | None
    streaming: list[str] | None
    every: int | None


class Config(TypedDict):
    embed: EmbedConfig | None


class Branding(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

        if config.get("status"):
            status: StatusConfig = config["status"]
            if not status.get("every"):
                status["every"] = 60 * 5
            assert isinstance(status["every"], int), "status.every must be an integer"

            @tasks.loop(seconds=status["every"])
            async def update_status_loop():
                try:
                    await self.update_status()
                except Exception as e:
                    logger.error(f"Error updating status: {e}")

            self.update_status_loop = update_status_loop

    @commands.Cog.listener()
    async def on_ready(self):
        if config.get("status"):
            self.update_status_loop.start()

    def cog_unload(self):
        if config.get("status"):
            self.update_status_loop.cancel()

    async def update_status(self):
        status_types = list(config["status"].keys())
        status_types.remove("every")
        status_type: str = random.choice(status_types)
        status: str = random.choice(config["status"][status_type])
        activity = discord.Activity(
            name=status,
            type=getattr(discord.ActivityType, status_type),
        )
        await self.bot.change_presence(activity=activity)


#    @tasks.loop(minutes=30)
#    async def update_count_loop(self):
#        try:
#            await self.update_count()
#        except Exception as e:
#            print(e)


def setup(bot: discord.Bot, logger_: logging.Logger, config_: dict):
    global logger
    global config
    logger = logger_
    config = config_

    logger.info("Loading Branding extension")

    if config.get("embed"):
        embed: EmbedConfig = config["embed"]
        footer: Footer | None = embed.get("footer")
        if footer:
            if footer_value := footer.get("value"):
                if isinstance(footer_value, str):
                    footer["value"]: list[str] = [footer_value]
            else:
                footer["value"]: list[str] = []
            if not footer.get("separator"):
                footer["separator"] = "|"
        if color := embed.get("color"):
            if isinstance(color, str):
                embed["color"]: str = color.lstrip("#")
                embed["color"]: int = int(embed["color"], 16)

        class Embed(discord.Embed):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                if footer:
                    value: list[str] = footer["value"].copy()
                    if footer.get("time"):
                        time: str = datetime.now(
                            pytz.timezone(footer.get("tz", "UTC"))
                        ).strftime(f"%d %B %Y at %H:%M ({footer.get('tz', 'UTC')})")
                        value.append(time)
                    self.set_footer(text=f" {footer['separator']} ".join(value))
                if embed.get("author"):
                    self.set_author(
                        name=embed["author"], icon_url=embed.get("author_url")
                    )
                if embed.get("color"):
                    self.color = discord.Color(embed["color"])

        discord.Embed = Embed

    bot.add_cog(Branding(bot))

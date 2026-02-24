# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

import logging
import random
from datetime import datetime
from typing import Any, cast, final

import discord
import pytz
from discord.ext import commands, tasks
from typing_extensions import TypedDict

from src.log import logger

BASE_URL = "https://top.gg/api"

logger: logging.Logger
default: dict[str, Any] = {  # pyright: ignore[reportExplicitAny]
    "enabled": True,
    "status": {
        "watching": ["you", "/help"],
        "every": 60 * 5,
    },
    "embed": {
        "footer": {
            "value": ["footer"],
            "time": True,
            "tz": "UTC",
            "separator": "|",
        },
        "color": 0x00FF00,
        "author": "Nice Bot",
        "author_url": "https://picsum.photos/512",
    },
}


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
    enabled: bool
    embed: EmbedConfig | None
    status: StatusConfig | None


@final
class Branding(discord.Cog):
    def __init__(self, bot: discord.Bot, config: Config) -> None:
        self.bot = bot
        self.config = config

        if status := self.config.get("status"):
            if not status.get("every"):
                status["every"] = 60 * 5
            if not isinstance(status["every"], int):
                raise AssertionError("status.every must be an integer")

            @tasks.loop(seconds=status["every"], reconnect=True)
            async def update_status_loop() -> None:
                await self.update_status()

            self.update_status_loop = update_status_loop

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        if self.config.get("status"):
            self.update_status_loop.start()

    def cog_unload(self) -> None:
        if self.config.get("status"):
            self.update_status_loop.cancel()

    async def update_status(self) -> None:
        status_types = list(self.config["status"].keys())  # pyright: ignore [reportOptionalMemberAccess]
        status_types.remove("every")
        status_type: str = random.choice(status_types)  # noqa: S311
        status: str = random.choice(self.config["status"][status_type])  # noqa: S311  # pyright: ignore [reportOptionalSubscript, reportUnknownArgumentType]
        activity = discord.Activity(
            name=status,
            type=getattr(discord.ActivityType, status_type),
        )
        await self.bot.change_presence(activity=activity)


def setup(bot: discord.Bot, config: dict[Any, Any]) -> None:
    if not config.get("embed") and not config.get("status"):
        logger.warning(
            "Branding extension is enabled but no configuration is provided for embed or status. You can disable this "
            "extension or provide a configuration in the config.yaml file.",
        )
    if config.get("embed"):
        embed: EmbedConfig = config["embed"]
        footer: Footer | None = embed.get("footer")
        if footer:
            if footer_value := footer.get("value"):
                if isinstance(footer_value, str):
                    footer["value"] = [footer_value]
            else:
                footer["value"] = []
            if not footer.get("separator"):
                footer["separator"] = "|"
        if (color := embed.get("color")) and isinstance(color, str):
            embed["color"] = color.lstrip("#")
            embed["color"] = int(embed["color"], 16)

        class Embed(discord.Embed):
            def __init__(self, **kwargs: Any) -> None:
                super().__init__(**kwargs)
                if footer:
                    value: list[str] = footer["value"].copy()  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                    if footer.get("time"):
                        time: str = datetime.now(pytz.timezone(footer.get("tz") or "UTC")).strftime(
                            f"%d %B %Y at %H:%M ({footer.get('tz', 'UTC')})",
                        )
                        value.append(time)
                    self.set_footer(text=f" {footer['separator']} ".join(value))
                if embed.get("author"):
                    self.set_author(name=embed["author"], icon_url=embed.get("author_url"))
                if embed.get("color") and not kwargs.get("color"):
                    self.color = discord.Color(embed["color"])  # pyright: ignore[reportArgumentType]

        discord.Embed = Embed

    bot.add_cog(Branding(bot, cast("Config", config)))  # pyright: ignore[reportInvalidCast]

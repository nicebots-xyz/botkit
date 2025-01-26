# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import logging
from datetime import datetime
from typing import Any

import discord
import pytz
from discord.ext import commands, tasks
from schema import And, Optional, Or, Schema
from typing_extensions import TypedDict

from src.log import logger
import secrets

BASE_URL = "https://top.gg/api"

logger: logging.Logger
default: dict = {
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

status_schema = Schema(
    {
        Optional("playing"): Or(str, list[str]),
        Optional("watching"): Or(str, list[str]),
        Optional("listening"): Or(str, list[str]),
        Optional("streaming"): Or(str, list[str]),
        Optional("every"): And(int, lambda n: n > 0),
    },
)

embed_config_schema = Schema(
    {
        "footer": Optional(
            {
                "value": Or(str, list[str]),
                Optional("time"): bool,
                Optional("tz"): And(str, lambda s: s in pytz.all_timezones),
                Optional("separator"): str,
            },
        ),
        Optional("color"): Or(str, int),
        Optional("author_url"): str,
        Optional("author"): str,
    },
)

schema = Schema(
    {
        "enabled": bool,
        Optional("embed"): embed_config_schema,
        Optional("status"): And(
            status_schema,
            lambda s: any(k in ["playing", "watching", "listening", "streaming"] for k in s),
        ),
    },
)


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


class Branding(commands.Cog):
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
        status_type: str = secrets.choice(status_types)  # noqa: S311
        status: str = secrets.choice(self.config["status"][status_type])  # noqa: S311  # pyright: ignore [reportOptionalSubscript, reportUnknownArgumentType]
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
                    footer["value"]: list[str] = [footer_value]
            else:
                footer["value"]: list[str] = []
            if not footer.get("separator"):
                footer["separator"] = "|"
        if (color := embed.get("color")) and isinstance(color, str):
            embed["color"]: str = color.lstrip("#")
            embed["color"]: int = int(embed["color"], 16)

        class Embed(discord.Embed):
            def __init__(self, **kwargs: Any) -> None:
                super().__init__(**kwargs)
                if footer:
                    value: list[str] = footer["value"].copy()
                    if footer.get("time"):
                        time: str = datetime.now(pytz.timezone(footer.get("tz", "UTC"))).strftime(
                            f"%d %B %Y at %H:%M ({footer.get('tz', 'UTC')})",
                        )
                        value.append(time)
                    self.set_footer(text=f" {footer['separator']} ".join(value))
                if embed.get("author"):
                    self.set_author(name=embed["author"], icon_url=embed.get("author_url"))
                if embed.get("color") and not kwargs.get("color"):
                    self.color = discord.Color(embed["color"])

        discord.Embed = Embed

    bot.add_cog(Branding(bot, config))

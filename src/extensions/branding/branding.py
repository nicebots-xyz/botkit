# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

import logging
import random
from typing import final, override

import discord
from discord.ext import commands, tasks
from typing_extensions import TypedDict

from src.log import logger

BASE_URL = "https://top.gg/api"

logger: logging.Logger


class StatusConfig(TypedDict, total=False):
    playing: list[str] | None
    watching: list[str] | None
    listening: list[str] | None
    streaming: list[str] | None
    custom: list[str] | None
    every: int | None


class Config(TypedDict, total=False):
    enabled: bool
    status: StatusConfig | None


default: Config = {
    "enabled": True,
    "status": {
        "custom": ["Watching you", "Try /help"],
        "every": 60 * 5,
    },
}


@final
class Branding(discord.Cog):
    def __init__(self, bot: discord.Bot, config: Config) -> None:
        self.bot = bot
        self.config = config

        if status := self.config.get("status"):
            if not status.get("every"):
                status["every"] = 60 * 5
            every = status.get("every")
            if not isinstance(every, int):
                raise AssertionError("status.every must be an integer")

            @tasks.loop(seconds=every, reconnect=True)
            async def update_status_loop() -> None:
                await self.update_status()

            self.update_status_loop = update_status_loop

    @commands.Cog.listener()  # pyright: ignore[reportUntypedFunctionDecorator]
    async def on_ready(self) -> None:
        if self.config.get("status"):
            self.update_status_loop.start()

    @override
    def cog_unload(self) -> None:
        if self.config.get("status"):
            self.update_status_loop.cancel()

    async def update_status(self) -> None:
        status_config = self.config.get("status")
        if not status_config:
            return

        statuses_by_type: dict[str, list[str]] = {
            status_type: statuses
            for status_type, statuses in status_config.items()
            if status_type != "every" and isinstance(statuses, list) and statuses
        }
        if not statuses_by_type:
            logger.warning("Branding extension is enabled but no status values are configured.")
            return

        status_type: str = random.choice(list(statuses_by_type))  # noqa: S311
        status: str = random.choice(statuses_by_type[status_type])  # noqa: S311
        if status_type == "custom":
            activity = discord.CustomActivity(name=status)
        else:
            activity = discord.Activity(
                name=status,
                type=getattr(discord.ActivityType, status_type),
            )
        await self.bot.change_presence(activity=activity)


def setup(bot: discord.Bot, config: Config) -> None:
    if not config.get("status"):
        logger.warning("Branding extension is enabled but no status configuration was provided.")

    bot.add_cog(Branding(bot, config))

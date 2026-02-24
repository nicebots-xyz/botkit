# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

import math
from typing import Any

import aiohttp
import discord
from discord.ext import commands, tasks

from src.log import logger

default = {
    "enabled": False,
    "url": "",
    "every": 60,
}


class Status(commands.Cog):
    def __init__(self, bot: discord.Bot, config: dict[Any, Any]) -> None:
        self.bot: discord.Bot = bot
        self.config: dict[Any, Any] = config
        self.push_status_loop: tasks.Loop = tasks.loop(seconds=self.config["every"])(self.push_status_loop_meth)  # pyright: ignore [reportMissingTypeArgument]
        super().__init__()

    @commands.Cog.listener(once=True)
    async def on_ready(self) -> None:
        self.push_status_loop.start()

    async def push_status_loop_meth(self) -> None:
        try:
            await self.push_status()
            logger.info("Pushed status.")
        except Exception:  # noqa: BLE001
            logger.exception("Failed to push status.")

    async def push_status(self) -> None:
        latency = self.bot.latency
        if latency == float("inf") or math.isnan(latency):
            logger.warning("Latency is infinite or NaN, skipping status push.")
            return
        ping = str(round(latency * 1000))
        async with aiohttp.ClientSession() as session, session.get(self.config["url"] + ping) as resp:
            resp.raise_for_status()


def setup(bot: discord.Bot, config: dict[Any, Any]) -> None:
    bot.add_cog(Status(bot, config))

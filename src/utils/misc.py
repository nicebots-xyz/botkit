# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT
from collections.abc import Callable

import discord


def mention_command(*command: str, bot: discord.Bot) -> str:
    command = " ".join(command)
    command = bot.get_application_command(command)
    if isinstance(command, discord.SlashCommand):
        return command.mention
    raise ValueError("Command not found")


class LazyProxy[T]:
    def __init__(self, func: Callable[..., T]) -> None:
        self._func: Callable[..., T] = func
        self._value: T | None = None

    def __getattr__(self, name: str) -> T:
        if self._value is None:
            self._value = self._func()
        return getattr(self._value, name)

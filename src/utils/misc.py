# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import discord


def mention_command(*command: str, bot: discord.Bot) -> str:
    command = " ".join(command)
    command = bot.get_application_command(command)
    if isinstance(command, discord.SlashCommand):
        return command.mention
    raise ValueError("Command not found")

# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

from typing import Any, final

import discord

from src.log import logger

default = {
    "enabled": True,
    "message": "Heyy, {user.mention}! Thank you for inviting me to your server! To get started, type `/help`",
}


@final
class AddDM(discord.Cog):
    def __init__(self, bot: discord.Bot, config: dict[str, Any]) -> None:
        self.bot = bot
        self.config = config
        super().__init__()

    @discord.Cog.listener("on_guild_join")
    async def on_join(self, guild: discord.Guild) -> None:
        if not guild.me.guild_permissions.view_audit_log:
            return

        entry = await guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add).flatten()
        user = entry[0].user
        if not user or user.bot:
            return
        try:
            await user.send(self.config["message"].format(user=user))
        except discord.Forbidden:
            logger.warning("Failed to send DM when joining a guild")


def setup(bot: discord.Bot, config: dict[str, Any]) -> None:
    bot.add_cog(AddDM(bot, config))

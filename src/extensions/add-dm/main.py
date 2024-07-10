import discord
import aiohttp

from quart import Quart
from discord.ext import commands
from schema import Schema
from src.logging import logger


default = {
    "enabled": True,
    "message": "Heyy, {user.mention}! Thank you for inviting me to your server! To get started, type `/help`",
}

schema = Schema(
    {
        "enabled": bool,
        "message": str,
    }
)


class AddDM(commands.Cog):
    def __init__(self, bot: discord.Bot, config: dict):
        self.bot = bot
        self.config = config

    @discord.Cog.listener("on_guild_join")
    async def on_join(self, guild: discord.Guild):
        if not guild.me.guild_permissions.view_audit_log:
            return

        entry = await guild.audit_logs(
            limit=1, action=discord.AuditLogAction.bot_add
        ).flatten()
        user = entry[0].user
        try:
            await user.send(self.config["message"].format(user=user))
        except discord.Forbidden:
            logger.warning(f"Failed to send DM when joining a guild")


def setup(bot: discord.Bot, config: dict) -> None:
    bot.add_cog(AddDM(bot, config))

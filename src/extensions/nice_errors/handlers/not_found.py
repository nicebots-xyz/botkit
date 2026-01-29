# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz


import contextlib
import difflib
from typing import Any, final, override

import discord
from discord.ext import bridge, commands

from src import custom
from src.i18n.classes import RawTranslation, apply_locale

from .base import BaseErrorHandler, ErrorHandlerRType


def find_most_similar(word: str, word_list: list[str]) -> str | None:
    if result := difflib.get_close_matches(word, word_list, n=1, cutoff=0.6):
        return result[0]
    return None


def find_similar_command(
    ctx: custom.ExtContext,
) -> bridge.BridgeExtCommand | commands.Command[Any, Any, Any] | None:
    command: str | None = ctx.invoked_with
    if not command:
        return None
    command_list: dict[str, bridge.BridgeExtCommand | commands.Command[Any, Any, Any]] = {
        cmd.name: cmd
        for cmd in ctx.bot.commands  # pyright: ignore[reportUnknownVariableType]
    }
    similar_command: str | None = find_most_similar(command, list(command_list.keys()))
    if similar_command:
        return command_list.get(similar_command)
    return None


class RunInsteadButton(discord.ui.Button[discord.ui.View]):
    def __init__(
        self,
        label: str,
        *,
        ctx: custom.ExtContext,
        instead: bridge.BridgeExtCommand | commands.Command[Any, Any, Any],
    ) -> None:
        self.ctx: custom.ExtContext = ctx
        self.instead: bridge.BridgeExtCommand | commands.Command[Any, Any, Any] = instead
        super().__init__(style=discord.ButtonStyle.green, label=label)

    @override
    async def callback(self, interaction: discord.Interaction) -> None:
        if not interaction.user or not self.ctx.author or interaction.user.id != self.ctx.author.id:
            await interaction.respond(":x: Nope", ephemeral=True)
            return
        await self.instead.invoke(self.ctx)
        await interaction.response.defer()
        if interaction.message:
            with contextlib.suppress(discord.HTTPException):
                await interaction.message.delete()


@final
class NotFoundErrorHandler(BaseErrorHandler[commands.CommandNotFound]):
    def __init__(self, translations: dict[str, RawTranslation]) -> None:
        self.translations = translations
        super().__init__(commands.CommandNotFound)

    @override
    async def __call__(
        self,
        error: commands.CommandNotFound,
        ctx: custom.Context | discord.Interaction,
        sendargs: dict[str, Any],
        message: str,
        report: bool,
    ) -> ErrorHandlerRType:
        if not isinstance(ctx, custom.ExtContext):
            return False, report, message, sendargs
        translations = apply_locale(self.translations, self._get_locale(ctx))
        if similar_command := find_similar_command(ctx):
            message = translations.error_command_not_found.format(similar_command=similar_command.name)
            view = discord.ui.View(
                RunInsteadButton(
                    translations.run_x_instead.format(command=similar_command.name),
                    ctx=ctx,
                    instead=similar_command,
                ),
                disable_on_timeout=True,
                timeout=60,  # 1 minute
            )
            sendargs["view"] = view
            return False, False, message, sendargs
        return True, False, message, sendargs

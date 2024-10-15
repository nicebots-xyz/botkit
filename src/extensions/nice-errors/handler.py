# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import discord

sentry_sdk = None

try:
    import sentry_sdk
except ImportError:
    pass


async def handle_error(
    error: Exception | discord.ApplicationCommandInvokeError,
    ctx: discord.ApplicationContext | discord.Interaction,
    use_sentry_sdk: bool = False,
):
    out = None
    original_error = error
    if use_sentry_sdk and sentry_sdk:
        out = sentry_sdk.capture_exception(error)
    if isinstance(error, discord.ApplicationCommandInvokeError):
        original_error = error.original
    if isinstance(error, discord.Forbidden):
        message = f"Whoops! I don't have the required permission to do that\n`{original_error.args[0].split(':')[-1].strip()}`"
    else:
        message = "Whoops! An error occurred while executing this command"
    if out:
        message += f"\n\n-# This error has been reported to the developers - `{out}`"
    await ctx.respond(message, ephemeral=True)  # pyright: ignore[reportUnknownMemberType]
    raise error

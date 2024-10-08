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
    if isinstance(error, discord.ApplicationCommandInvokeError):
        await ctx.respond(  # pyright: ignore[reportUnknownMemberType]
            f"Whoops! I don't have permission to do that\n`{error.original.args[0].split(':')[-1].strip()}`",
            ephemeral=True,
        )
    else:
        await ctx.respond(  # pyright: ignore[reportUnknownMemberType]
            "Whoops! An error occurred while executing this command", ephemeral=True
        )
    if use_sentry_sdk and sentry_sdk:
        sentry_sdk.capture_exception(error)
    raise

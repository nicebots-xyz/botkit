import discord
from discord import Interaction
from discord.ui import Item
from typing_extensions import override


def patch():

    class PatchedView(discord.ui.View):

        @override
        async def on_error(
            self,
            error: Exception,
            item: Item,  # pyright: ignore[reportMissingTypeArgument,reportUnknownParameterType]
            interaction: Interaction,
        ) -> None:
            if not isinstance(error, discord.Forbidden):
                await interaction.respond(  # pyright: ignore[reportUnknownMemberType]
                    "Whoops! An error occurred while executing this command",
                    ephemeral=True,
                )
                raise error
            await interaction.respond(  # pyright: ignore[reportUnknownMemberType]
                f"Whoops! I don't have permission to do that\n`{error.args[0].split(':')[-1].strip()}`",
                ephemeral=True,
            )

    discord.ui.View = PatchedView

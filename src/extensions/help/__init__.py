# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

from collections import defaultdict
from functools import cached_property
from typing import Any, Final, final

import discord
from discord.ext import commands
from discord.ui import ActionRow, Button, Container, DesignerView, Select, TextDisplay

from src import custom
from src.extensions.help.pages.classes import (
    HelpCategoryTranslation,
)
from src.i18n.classes import RawTranslation, TranslationWrapper, apply_locale

from .pages import help_translation


def get_gradient_color(shade_index: int, color_index: int, max_shade: int = 50, max_color: int = 10) -> int:
    """Generate a color from a two-dimensional gradient system using bright pastel colors.

    Args:
    ----
        shade_index (int): Index for shade selection (0 to max_shade)
        color_index (int): Index for base color selection (0 to max_color)
        max_shade (int): Maximum value for shade_index (default 50)
        max_color (int): Maximum value for color_index (default 10)

    Returns:
    -------
        int: Color as a 24-bit integer

    """
    # Normalize indices to 0-1 range
    shade_factor = max(0, min(1, shade_index / max_shade))
    color_factor = max(0, min(1, color_index / max_color))

    # Bright pastel base colors
    base_colors = [
        (179, 229, 252),  # Bright light blue
        (225, 190, 231),  # Bright lilac
        (255, 209, 220),  # Bright pink
        (255, 224, 178),  # Bright peach
        (255, 255, 198),  # Bright yellow
        (200, 230, 201),  # Bright mint
        (178, 255, 255),  # Bright turquoise
        (187, 222, 251),  # Bright baby blue
        (225, 190, 231),  # Bright lavender
        (255, 236, 179),  # Bright cream
        (200, 230, 255),  # Bright sky blue
    ]

    # Interpolate between colors based on color_factor
    color_index_float = color_factor * (len(base_colors) - 1)
    color_index_low = int(color_index_float)
    color_index_high = min(color_index_low + 1, len(base_colors) - 1)
    color_blend = color_index_float - color_index_low

    c1 = base_colors[color_index_low]
    c2 = base_colors[color_index_high]

    # Interpolate between the two closest base colors
    base_color = tuple(int(c1[i] * (1 - color_blend) + c2[i] * color_blend) for i in range(3))

    # Modified shading approach for brighter colors
    if shade_factor < 0.5:
        # Darker shades: interpolate towards a very light gray instead of black
        shade_factor_adjusted = shade_factor * 2
        # Increase minimum brightness (was 120, now 180)
        darker_tone = tuple(max(c * 0.8, 180) for c in base_color)
        final_color = tuple(
            int(darker_tone[i] + (base_color[i] - darker_tone[i]) * shade_factor_adjusted) for i in range(3)
        )
    else:
        # Lighter shades: interpolate towards white
        shade_factor_adjusted = (shade_factor - 0.5) * 2
        final_color = tuple(
            int(base_color[i] * (1 - shade_factor_adjusted) + 255 * shade_factor_adjusted) for i in range(3)
        )

    # Convert to 24-bit integer
    return (final_color[0] << 16) | (final_color[1] << 8) | final_color[2]


@final
class HelpView(DesignerView):
    def __init__(
        self,
        categories_data: dict[str, list[dict]],  # pyright: ignore[reportMissingTypeArgument]
        ui_translations: TranslationWrapper[dict[str, RawTranslation]],
        bot: custom.Bot,
    ) -> None:
        super().__init__(timeout=180)
        self.bot = bot
        self.categories_data = categories_data
        self.ui_translations = ui_translations
        self.current_category = next(iter(categories_data.keys()))
        self.current_page = 0
        self.total_pages = len(categories_data[self.current_category])

        # Create navigation buttons (will be added to container in update_content)
        self.first_button = Button(style=discord.ButtonStyle.blurple, emoji="⏮️", label="First", disabled=True)
        self.first_button.callback = self.first_button_callback

        self.prev_button = Button(style=discord.ButtonStyle.red, emoji="◀️", label="Previous", disabled=True)
        self.prev_button.callback = self.prev_button_callback

        self.page_indicator = Button(
            style=discord.ButtonStyle.gray,
            label=ui_translations.page_indicator.format(current=1, total=self.total_pages),
            disabled=True,
        )

        self.next_button = Button(
            style=discord.ButtonStyle.green, emoji="▶️", label="Next", disabled=self.total_pages <= 1
        )
        self.next_button.callback = self.next_button_callback

        self.last_button = Button(
            style=discord.ButtonStyle.blurple, emoji="⏭️", label="Last", disabled=self.total_pages <= 1
        )
        self.last_button.callback = self.last_button_callback

        # Create category selector
        self.category_select = Select(
            placeholder=ui_translations.select_category,
            options=[discord.SelectOption(label=category, value=category) for category in categories_data],
        )
        self.category_select.callback = self.category_select_callback

        # Add the main container with content
        self.update_content()

    def update_content(self) -> None:
        """Update the view's content based on the current category and page."""
        # Remove existing containers if any
        for item in list(self.children):
            if isinstance(item, Container):
                self.remove_item(item)

        # Get the current page data
        page_data = self.categories_data[self.current_category][self.current_page]

        # Create the main container
        container = Container(color=discord.Color(page_data["color"]))

        # Add title directly as TextDisplay
        title_text = TextDisplay(f"### {page_data['title']}")
        container.add_item(title_text)

        # Add description directly as TextDisplay
        description_text = TextDisplay(page_data["description"])
        container.add_item(description_text)

        # Add separator
        container.add_separator(divider=True)

        # Add quick tips if available
        if page_data.get("quick_tips"):
            tips_title = TextDisplay(f"### {self.ui_translations.quick_tips_title}")
            container.add_item(tips_title)
            tips_content = TextDisplay("\n".join([f"- {tip}" for tip in page_data["quick_tips"]]))
            container.add_item(tips_content)
            container.add_separator()

        # Add examples if available
        if page_data.get("examples"):
            examples_title = TextDisplay(f"### {self.ui_translations.examples_title}")
            container.add_item(examples_title)
            examples_content = TextDisplay("\n".join([f"- {example}" for example in page_data["examples"]]))
            container.add_item(examples_content)
            container.add_separator()

        # Add related commands if available
        if page_data.get("related_commands"):
            commands_title = TextDisplay(f"### {self.ui_translations.related_commands_title}")
            commands_content_list = []
            for cmd_name in page_data["related_commands"]:
                cmd = self.bot.get_application_command(cmd_name)
                if cmd:
                    commands_content_list.append(f"- {cmd.mention}")  # pyright: ignore[reportAttributeAccessIssue]
            if commands_content_list:
                container.add_item(commands_title)
                commands_content = TextDisplay("\n".join(commands_content_list))
                container.add_item(commands_content)
                container.add_separator(divider=True)

        # Add navigation buttons to the container
        container.add_item(
            ActionRow(self.first_button, self.prev_button, self.page_indicator, self.next_button, self.last_button)
        )
        container.add_item(ActionRow(self.category_select))

        # Add the container to the view
        self.add_item(container)

    async def category_select_callback(self, interaction: discord.Interaction) -> None:
        """Handle category selection."""
        self.current_category = self.category_select.values[0]
        self.current_page = 0
        self.total_pages = len(self.categories_data[self.current_category])

        # Update navigation buttons
        self.first_button.disabled = True
        self.prev_button.disabled = True
        self.next_button.disabled = self.total_pages <= 1
        self.last_button.disabled = self.total_pages <= 1
        self.page_indicator.label = self.ui_translations.page_indicator.format(current=1, total=self.total_pages)

        # Update content
        self.update_content()
        await interaction.response.edit_message(view=self)

    async def first_button_callback(self, interaction: discord.Interaction) -> None:
        """Go to the first page."""
        self.current_page = 0
        await self.update_page(interaction)

    async def prev_button_callback(self, interaction: discord.Interaction) -> None:
        """Go to the previous page."""
        self.current_page = max(0, self.current_page - 1)
        await self.update_page(interaction)

    async def next_button_callback(self, interaction: discord.Interaction) -> None:
        """Go to the next page."""
        self.current_page = min(self.total_pages - 1, self.current_page + 1)
        await self.update_page(interaction)

    async def last_button_callback(self, interaction: discord.Interaction) -> None:
        """Go to the last page."""
        self.current_page = self.total_pages - 1
        await self.update_page(interaction)

    async def update_page(self, interaction: discord.Interaction) -> None:
        """Update the view after a page change."""
        # Update navigation buttons
        self.first_button.disabled = self.current_page == 0
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == self.total_pages - 1
        self.last_button.disabled = self.current_page == self.total_pages - 1
        self.page_indicator.label = self.ui_translations.page_indicator.format(
            current=self.current_page + 1, total=self.total_pages
        )

        # Update content
        self.update_content()
        await interaction.response.edit_message(view=self)


def get_categories_data(
    ui_translations: TranslationWrapper[dict[str, RawTranslation]],  # noqa: ARG001
    categories: dict[str, TranslationWrapper[HelpCategoryTranslation]],
    bot: custom.Bot,  # noqa: ARG001
) -> dict[str, list[dict[str, Any]]]:
    """Generate category data for the help view.

    Returns a dictionary where keys are category names and values are lists of page data dictionaries.
    Each page data dictionary contains title, description, color, and optional quick_tips,
    examples, and related_commands.
    """
    categories_data: defaultdict[str, list[dict]] = defaultdict(list)  # pyright: ignore[reportMissingTypeArgument]
    for i, category in enumerate(categories):
        for j, page in enumerate(category.pages.values()):  # pyright: ignore [reportUnknownArgumentType, reportUnknownVariableType, reportAttributeAccessIssue]
            page_data = {
                "title": f"{category.name} - {page.title}",  # pyright: ignore [reportAttributeAccessIssue]
                "description": page.description,
                "color": get_gradient_color(i, j),
            }

            if page.quick_tips:
                page_data["quick_tips"] = page.quick_tips

            if page.examples:
                page_data["examples"] = page.examples

            if page.related_commands:
                page_data["related_commands"] = page.related_commands

            categories_data[category.name].append(page_data)  # pyright: ignore [reportAttributeAccessIssue]

    return dict(categories_data)  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]


@final
class Help(commands.Cog):
    def __init__(self, bot: custom.Bot, ui_translations: dict[str, RawTranslation], locales: set[str]) -> None:
        self.bot = bot
        self.ui_translations = ui_translations
        self.locales = locales
        super().__init__()

    @cached_property
    def categories_data(self) -> dict[str, dict[str, list[dict]]]:  # pyright: ignore[reportMissingTypeArgument]
        """Generate and cache help category data for all locales."""
        data: defaultdict[str, dict[str, list[dict]]] = defaultdict(dict)  # pyright: ignore[reportMissingTypeArgument]
        for locale in self.locales:
            t = help_translation.get_for_locale(locale)
            ui = apply_locale(self.ui_translations, locale)
            data[locale] = get_categories_data(ui, t.categories, self.bot)
        return dict(data)

    @discord.slash_command(
        name="help",
        integration_types={discord.IntegrationType.user_install, discord.IntegrationType.guild_install},
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.private_channel,
            discord.InteractionContextType.bot_dm,
        },
    )
    async def help_slash(self, ctx: custom.ApplicationContext) -> None:
        """Display help information using the new UI components."""
        help_view = HelpView(
            categories_data=self.categories_data.get(ctx.locale or "") or self.categories_data["en-US"],
            ui_translations=apply_locale(self.ui_translations, ctx.locale),
            bot=self.bot,
        )
        await ctx.respond(view=help_view, ephemeral=True)


def setup(bot: custom.Bot, config: dict[str, Any]) -> None:  # pyright: ignore [reportExplicitAny]
    bot.add_cog(Help(bot, config["translations"], set(config["locales"])))


default: Final = {"enabled": False}
__all__ = ["default", "setup"]

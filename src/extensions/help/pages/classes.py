# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz


from src.i18n.classes import RawTranslation, Translation


class HelpPageTranslation(Translation):
    title: RawTranslation
    description: RawTranslation
    category: RawTranslation
    quick_tips: list[RawTranslation] | None = None
    examples: list[RawTranslation] | None = None
    related_commands: list[str] | None = None


class HelpCategoryTranslation(Translation):
    name: RawTranslation
    description: RawTranslation
    pages: dict[str, HelpPageTranslation]
    order: int  # For sorting categories in the dropdown


class HelpTranslation(Translation):
    categories: list[HelpCategoryTranslation]

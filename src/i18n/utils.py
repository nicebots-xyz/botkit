# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

from typing import TypeVar, TYPE_CHECKING
import discord

from .classes import (
    ExtensionTranslation,
    Deg1CommandTranslation,
    Deg2CommandTranslation,
)
from src.log import logger as main_logger
import yaml
from discord.ext import commands as prefixed

if TYPE_CHECKING:
    from src import custom
logger = main_logger.getChild("i18n")


T = TypeVar("T")
V = TypeVar("V")


def remove_none(d: dict[T, V]) -> dict[T, V]:
    """Remove None values from a dictionary.

    Args:
        d (dict[T, V]): The dictionary to remove None values from.

    Returns:
        dict[T, V]: The dictionary without None values.
    """
    return {k: v for k, v in d.items() if v is not None}


def merge_command_translations(
    translations: list[ExtensionTranslation],
) -> dict[str, Deg1CommandTranslation] | None:
    """Merge command translations into a single dictionary.

    Args:
        translations (list[ExtensionTranslation]): A list of translations.

    Returns:
        dict[str, Deg1CommandTranslation] | None: A dictionary of command translations.

    Raises:
        None
    """
    command_translations: list[dict[str, Deg1CommandTranslation]] = [
        t.commands for t in translations if t.commands
    ]
    if not command_translations:
        return None
    result: dict[str, Deg1CommandTranslation] = {}
    for translation in command_translations:
        for command_name, command_translation in translation.items():
            if command_name not in result:
                result[command_name] = command_translation
            else:
                logger.warning(f"Command {command_name} is already defined, skipping")
    return result


CommandT = TypeVar(
    "CommandT",
    discord.ApplicationCommand,  # pyright: ignore[reportMissingTypeArgument]
    discord.SlashCommand,
    discord.SlashCommandGroup,
    prefixed.Command,  # pyright: ignore[reportMissingTypeArgument]
)


def localize_commands(
    commands: list[CommandT],
    translations: ExtensionTranslation
    | Deg1CommandTranslation
    | Deg2CommandTranslation
    | dict[str, Deg1CommandTranslation],
    DEFAULT_LOCALE: str = "en-US",
) -> tuple[int, int]:
    """Recursively localize commands and their subcommands.

    Args:
        commands: List of commands to localize.
        translations: Translations for the commands.
        DEFAULT_LOCALE: The default locale to use.

    Returns:
        None
    """
    logger.info("Localizing commands...")
    err = 0
    tot = 0
    for command in commands:
        if isinstance(
            command, (discord.SlashCommand, discord.SlashCommandGroup, prefixed.Command)
        ):
            tot += 1
            try:
                try:
                    if isinstance(translations, dict):
                        translatable = translations
                    else:
                        translatable = translations.commands
                    if translatable:
                        translation = translatable.get(command.name)
                        if not translation:
                            raise AttributeError
                    else:
                        raise AttributeError
                except AttributeError:
                    logger.warning(
                        f"Command /{command.qualified_name} is not defined in translations, continuing..."
                    )
                    err += 1
                    continue
                if translation.name:
                    name = remove_none(translation.name.model_dump(by_alias=True))
                    command.name = name.get(DEFAULT_LOCALE, command.name)
                    if not isinstance(command, prefixed.Command):
                        command.name_localizations = name
                if translation.description:
                    description = remove_none(
                        translation.description.model_dump(by_alias=True)
                    )
                    command.description = description.get(
                        DEFAULT_LOCALE, command.description
                    )
                    if not isinstance(command, prefixed.Command):
                        command.description_localizations = description
                if translation.strings:
                    command.translations = translation.strings  # pyright: ignore[reportAttributeAccessIssue]
                if isinstance(command, discord.SlashCommand) and translation.options:
                    for option in command.options:
                        if option.name in translation.options:
                            opt = translation.options[option.name]
                            if opt.name:
                                name = remove_none(opt.name.model_dump(by_alias=True))
                                option.name = name.get(DEFAULT_LOCALE, option.name)
                                option.name_localizations = name
                            if opt.description:
                                description = remove_none(
                                    opt.description.model_dump(by_alias=True)
                                )
                                option.description = description.get(
                                    DEFAULT_LOCALE, option.description
                                )
                                option.description_localizations = description
                        else:
                            logger.warning(
                                f"Option {option.name} of command /{command.qualified_name} is not defined in translations, continuing..."
                            )
                if isinstance(command, discord.SlashCommandGroup) and isinstance(
                    translation, (Deg1CommandTranslation, Deg2CommandTranslation)
                ):
                    localize_commands(command.subcommands, translation, DEFAULT_LOCALE)
            except Exception as e:
                logger.error(f"Error localizing command /{command.name}: {e}")
                err += 1
    return err, tot


def load_translation(path: str) -> ExtensionTranslation:
    """Load a translation from a file.

    Args:
        path (str): The path to the translation file.

    Returns:
        ExtensionTranslation: The loaded translation.

    Raises:
        yaml.YAMLError: If the file is not a valid YAML file.
    """

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return ExtensionTranslation(**data)


def apply(
    bot: "custom.Bot",
    translations: list[ExtensionTranslation],
    DEFAULT_LOCALE: str = "en-US",
) -> None:
    """Apply translations to the bot.

    Args:
        bot: The bot to apply translations to.
        translations: The translations to apply.
        DEFAULT_LOCALE: The default locale to use.

    Returns:
        None
    """
    logger.info("Applying translations")
    command_translations = merge_command_translations(translations)
    if command_translations is None:
        logger.warning("No command translations found, skipping...")
        return

    err, tot = localize_commands(
        [*bot.pending_application_commands, *bot.commands],  # pyright: ignore[reportUnknownMemberType,reportUnknownArgumentType]
        command_translations,
        DEFAULT_LOCALE,
    )
    if tot == err:
        logger.error(f"Localized {tot - err}/{tot} commands.")
    elif err:
        logger.warning(f"Localized {tot - err}/{tot} commands.")
    else:
        logger.success(f"Localized {tot}/{tot} commands.")

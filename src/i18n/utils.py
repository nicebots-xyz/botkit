# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

from collections.abc import Iterable, Iterator, Mapping
from pathlib import Path
from typing import Any, override

import discord
import yaml
from discord.ext import bridge
from discord.ext import commands as prefixed

from src.log import logger as main_logger

from .classes import (
    Deg1CommandTranslation,
    Deg2CommandTranslation,
    ExtensionTranslation,
    add_global_kv,
)

logger = main_logger.getChild("i18n")

type AppCommand = discord.ApplicationCommand[Any, ..., Any]


def _walk(commands: Iterable[AppCommand]) -> Iterator[AppCommand]:
    for command in commands:
        yield command
        if isinstance(command, discord.SlashCommandGroup):
            yield from _walk(command.subcommands)


class CommandMapping(Mapping[str, str]):
    def __init__(self, bot: bridge.Bot) -> None:
        """Map ``{commands.x}`` placeholders to the bot's application commands.

        Args:
            bot: Bot whose pending application commands are mapped.

        """
        self.bot: bridge.Bot = bot

    def _commands(self) -> dict[str, AppCommand]:
        pending: list[AppCommand] = self.bot.pending_application_commands  # pyright: ignore[reportUnknownVariableType]
        return {command.qualified_name.replace(" ", "__"): command for command in _walk(pending)}

    @override
    def __getitem__(self, key: str) -> str:
        """Resolve a command key, with subcommands separated by ``__``.

        Args:
            key: Command key, e.g. ``admin__kick``.

        Returns:
            The command mention for slash commands, otherwise the command name.

        Raises:
            KeyError: If the command does not exist, or is a slash command that is not synced yet.

        """
        command = self._commands()[key]
        if not isinstance(command, discord.SlashCommand):
            return command.name
        try:
            return command.mention
        except AttributeError as e:  # unsynced commands have no id to mention them with
            raise KeyError(key) from e

    @override
    def __contains__(self, key: object) -> bool:
        return key in self._commands()

    @override
    def __iter__(self) -> Iterator[str]:
        return iter(self._commands())

    @override
    def __len__(self) -> int:
        return len(self._commands())


class EmojiMapping(Mapping[str, str]):
    def __init__(self, bot: bridge.Bot) -> None:
        """Map ``{emojis.x}`` placeholders to the bot's application emojis.

        Args:
            bot: Bot whose cached application emojis are mapped.

        """
        self.bot: bridge.Bot = bot

    def _emojis(self) -> dict[str, str]:
        return {emoji.name: emoji.mention for emoji in self.bot.app_emojis}

    @override
    def __getitem__(self, key: str) -> str:
        return self._emojis()[key]

    @override
    def __iter__(self) -> Iterator[str]:
        return iter(self._emojis())

    @override
    def __len__(self) -> int:
        return len(self._emojis())


def merge_command_translations(
    translations: list[ExtensionTranslation],
) -> dict[str, Deg1CommandTranslation] | None:
    """Merge command translations into a single dictionary.

    Args:
    ----
        translations (list[ExtensionTranslation]): A list of translations.

    Returns:
    -------
        dict[str, Deg1CommandTranslation] | None: A dictionary of command translations.

    Raises:
    ------
        None

    """
    command_translations: list[dict[str, Deg1CommandTranslation]] = [t.commands for t in translations if t.commands]
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


def localize_commands[  # noqa: PLR0912
    T: (
        discord.ApplicationCommand,  # pyright: ignore[reportMissingTypeArgument]
        discord.SlashCommand,
        discord.SlashCommandGroup,
        prefixed.Command,  # pyright: ignore[reportMissingTypeArgument]
        discord.MessageCommand,
        discord.UserCommand,
    )
](
    commands: list[T],
    translations: ExtensionTranslation
    | Deg1CommandTranslation
    | Deg2CommandTranslation
    | dict[str, Deg1CommandTranslation],
    default_locale: str = "en-US",
) -> tuple[int, int]:
    """Recursively localize commands and their subcommands.

    Args:
    ----
        commands: List of commands to localize.
        translations: Translations for the commands.
        default_locale: The default locale to use.

    Returns:
    -------
        None

    """
    logger.info("Localizing commands...")
    err = 0
    tot = 0
    for command in commands:
        if isinstance(
            command,
            discord.SlashCommand
            | discord.SlashCommandGroup
            | prefixed.Command
            | discord.MessageCommand
            | discord.UserCommand,
        ):
            tot += 1
            try:
                try:
                    translatable = translations if isinstance(translations, dict) else translations.commands
                    if translatable:
                        translation = translatable.get(command.name)
                        if not translation:
                            raise AttributeError  # noqa: TRY301
                    else:
                        raise AttributeError  # noqa: TRY301
                except AttributeError:
                    logger.warning(f"Command /{command.qualified_name} is not defined in translations, continuing...")
                    err += 1
                    continue
                if translation.name:
                    name = translation.name.root
                    command.name = name.get(default_locale, command.name)
                    if not isinstance(command, prefixed.Command):
                        command.name_localizations = name
                if translation.description:
                    description = translation.description.root
                    command.description = description.get(default_locale, command.description)
                    if not isinstance(command, prefixed.Command):
                        command.description_localizations = description  # pyright: ignore [reportAttributeAccessIssue]
                if translation.strings:
                    command.translations = translation.strings  # pyright: ignore[reportAttributeAccessIssue]
                if isinstance(command, discord.SlashCommand) and translation.options:
                    for option in command.options:
                        if option.name in translation.options:
                            opt = translation.options[option.name]
                            if opt.name:
                                name = opt.name.root
                                option.name = name.get(default_locale, option.name)
                                option.name_localizations = name
                            if opt.description:
                                description = opt.description.root
                                option.description = description.get(default_locale, option.description)
                                option.description_localizations = description
                        else:
                            logger.warning(
                                f"Option {option.name} of command /{command.qualified_name} is not defined in translations, continuing...",  # noqa: E501
                            )
                if isinstance(command, discord.SlashCommandGroup) and isinstance(
                    translation,
                    Deg1CommandTranslation | Deg2CommandTranslation,
                ):
                    localize_commands(command.subcommands, translation, default_locale)
            except Exception:
                logger.exception(f"Error localizing command /{command.name}")
                err += 1
    return err, tot


def find_translation_file(extension_path: Path, extension_name: str) -> Path | None:
    """Find the translation file or folder of an extension.

    Searches, in order, ``translations.yml``, ``translations.yaml`` and a ``translations`` folder, first in the
    extension's directory and then as ``src/translations/{extension_name}``.

    Args:
        extension_path: Path to the extension directory.
        extension_name: Name of the extension.

    Returns:
        Path to the translation file or folder if found, None otherwise.

    """
    for base in (extension_path / "translations", Path(__file__).parent.parent / "translations" / extension_name):
        for candidate in (base.with_suffix(".yml"), base.with_suffix(".yaml"), base):
            if candidate.exists():
                return candidate
    return None


def _read_yaml_tree(path: Path) -> Any:
    """Read a YAML file, or a folder whose files and subfolders become nested keys named after them.

    Args:
        path: The YAML file or folder to read.

    Returns:
        The parsed data.

    """
    if path.is_file():
        with path.open(encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {
        child.stem: _read_yaml_tree(child)
        for child in sorted(path.iterdir())
        if child.is_dir() or child.suffix in {".yml", ".yaml"}
    }


def load_translation(path: str | Path) -> ExtensionTranslation:
    """Load a translation from a file or a folder.

    In a folder, ``commands/ping.yml`` is equivalent to a ``ping`` key under ``commands`` in a single file.

    Args:
        path: The path to the translation file or folder.

    Returns:
        The loaded translation.

    Raises:
        yaml.YAMLError: If a file is not a valid YAML file.

    """
    return ExtensionTranslation.model_validate(_read_yaml_tree(Path(path)))


def apply(
    bot: bridge.Bot,
    translations: list[ExtensionTranslation],
    default_locale: str = "en-US",
) -> None:
    """Apply translations to the bot.

    Args:
    ----
        bot: The bot to apply translations to.
        translations: The translations to apply.
        default_locale: The default locale to use.

    Returns:
    -------
        None

    """
    logger.info("Applying translations")
    add_global_kv("commands", CommandMapping(bot))
    add_global_kv("emojis", EmojiMapping(bot))
    command_translations = merge_command_translations(translations)
    if command_translations is None:
        logger.warning("No command translations found, skipping...")
        return

    err, tot = localize_commands(
        [*bot.pending_application_commands, *bot.commands],  # pyright: ignore[reportUnknownArgumentType]
        command_translations,
        default_locale,
    )
    if tot == err:
        logger.error(f"Localized {tot - err}/{tot} commands.")
    elif err:
        logger.warning(f"Localized {tot - err}/{tot} commands.")
    else:
        logger.success(f"Localized {tot}/{tot} commands.")

# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

from collections.abc import Iterable, Iterator, Mapping
from pathlib import Path
from typing import Any, cast, override

import discord
import yaml
from pydantic import BaseModel

from src.log import logger as main_logger

from .classes import (
    DEFAULT,
    DEFER_FIELD_CHECKS,
    Deg1CommandTranslation,
    Deg2CommandTranslation,
    ExtensionTranslation,
    RawTranslation,
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
    def __init__(self, bot: discord.Bot) -> None:
        """Map ``{commands.x}`` placeholders to the bot's application commands.

        Args:
            bot: Bot whose pending application commands are mapped.

        """
        self.bot: discord.Bot = bot

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
    def __init__(self, bot: discord.Bot) -> None:
        """Map ``{emojis.x}`` placeholders to the bot's application emojis.

        Args:
            bot: Bot whose cached application emojis are mapped.

        """
        self.bot: discord.Bot = bot

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
            discord.SlashCommand | discord.SlashCommandGroup | discord.MessageCommand | discord.UserCommand,
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
                    command.name_localizations = name
                if translation.description:
                    description = translation.description.root
                    command.description = description.get(default_locale, command.description)
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


TRANSLATIONS = Path(__file__).parent.parent / "translations"


def _find(base: Path) -> Path | None:
    """Find a translation file or folder, trying ``.yml``, ``.yaml`` and then a folder.

    Args:
        base: Path of the translation, without extension.

    Returns:
        The first existing candidate, None if there is none.

    """
    return next((c for c in (base.with_suffix(".yml"), base.with_suffix(".yaml"), base) if c.exists()), None)


def find_translation_files(extension_path: Path, extension_name: str) -> list[Path]:
    """Find the translation layers of an extension, from the one defining its strings to the bot's overrides.

    The extension's own ``translations`` file or folder comes first, followed by the bot's
    ``src/translations/{extension_name}`` one. The first layer is the extension's contract: it defines the strings
    and their format arguments, from which its stubs are generated. Later layers adapt them to the bot.

    Args:
        extension_path: Path to the extension directory.
        extension_name: Name of the extension.

    Returns:
        The existing layers, in the order they apply.

    """
    candidates = (_find(extension_path / "translations"), _find(TRANSLATIONS / extension_name))
    return [path for path in candidates if path is not None]


def _read_yaml_tree(path: Path) -> object:
    """Read a YAML file, or a folder whose files and subfolders become nested keys named after them.

    Args:
        path: The YAML file or folder to read.

    Returns:
        The parsed data.

    """
    if path.is_file():
        with path.open(encoding="utf-8") as f:
            return cast("object", yaml.safe_load(f)) or {}
    return {
        child.stem: _read_yaml_tree(child)
        for child in sorted(path.iterdir())
        if child.is_dir() or child.suffix in {".yml", ".yaml"}
    }


def _merge(base: object, override: object) -> object:
    """Deep merge two parsed translation trees.

    Mappings are merged key by key, so an override can translate a single locale of a string.
    Any other value of the override replaces the base one.

    Args:
        base: The tree to override.
        override: The tree whose values take precedence.

    Returns:
        The merged tree.

    """
    if not isinstance(base, Mapping) or not isinstance(override, Mapping):
        return override
    merged = dict(cast("Mapping[str, object]", base))
    for key, value in cast("Mapping[str, object]", override).items():
        merged[key] = _merge(merged[key], value) if key in merged else value
    return merged


def _raw_translations(value: object, path: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], RawTranslation]]:
    """Walk a translation tree, yielding every raw translation with the keys leading to it.

    Args:
        value: A translation, a mapping of them, or any other value.
        path: Keys leading to ``value``.

    Yields:
        The keys leading to each raw translation, and the raw translation.

    """
    if isinstance(value, RawTranslation):
        yield path, value
        return
    if isinstance(value, BaseModel):
        value = dict(value)
    if isinstance(value, Mapping):
        for key, item in cast("Mapping[str, object]", value).items():
            yield from _raw_translations(item, (*path, key))


def _reference_text(tree: object, path: tuple[str, ...]) -> str | None:
    """Get the default text of a string in a parsed translation tree.

    Args:
        tree: The parsed tree.
        path: Keys leading to the string.

    Returns:
        The string's default text, None if the tree does not define it.

    """
    for key in path:
        if not isinstance(tree, Mapping):
            return None
        tree = cast("Mapping[str, object]", tree).get(key)
    if isinstance(tree, Mapping) and isinstance(text := cast("Mapping[str, object]", tree).get(DEFAULT), str):
        return text
    return None


def load_translation(*paths: str | Path) -> ExtensionTranslation:
    """Load a translation from files or folders, each one overriding the previous ones.

    In a folder, ``commands/ping.yml`` is equivalent to a ``ping`` key under ``commands`` in a single file.

    The first path defines the strings, which later ones may translate, reword or add to. Code and stubs format a
    string with the arguments of its text in the first path, so an override may not use other ones.

    Args:
        *paths: The paths to the translation files or folders, from the base one to the last override.

    Returns:
        The merged translation.

    Raises:
        yaml.YAMLError: If a file is not a valid YAML file.
        ValueError: If no path is given, or an override uses format arguments its base string does not.

    """
    if not paths:
        raise ValueError("At least one translation path is required")
    base, *overrides = (_read_yaml_tree(Path(path)) for path in paths)
    merged = base
    for layer in overrides:
        merged = _merge(merged, layer)
    if not overrides:
        return ExtensionTranslation.model_validate(base)
    translation = ExtensionTranslation.model_validate(merged, context={DEFER_FIELD_CHECKS: True})
    for path, raw in _raw_translations(translation):
        # Strings only defined by overrides are not part of the contract, and are formatted like their default text.
        reference = _reference_text(base, path)
        try:
            if reference is None:
                raw.check_fields(raw.root[DEFAULT])
            else:
                raw.check_fields(reference, f"the {DEFAULT} text of {Path(paths[0])}")
        except ValueError as e:
            raise ValueError(f"{'.'.join(path)}: {e}") from e
    return translation


def apply(
    bot: discord.Bot,
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
        bot.pending_application_commands,  # pyright: ignore[reportUnknownArgumentType]
        command_translations,
        default_locale,
    )
    if tot == err:
        logger.error(f"Localized {tot - err}/{tot} commands.")
    elif err:
        logger.warning(f"Localized {tot - err}/{tot} commands.")
    else:
        logger.success(f"Localized {tot}/{tot} commands.")

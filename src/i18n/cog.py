# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz
from collections.abc import Iterator, Mapping
from datetime import timedelta
from typing import TYPE_CHECKING, override

import discord
from cachetools import TTLCache

from src.log import logger as main_logger

from .classes import add_global_kv

if TYPE_CHECKING:
    from src import custom
logger = main_logger.getChild("i18n")


class AppCommandMapping(Mapping[str, str]):
    def __init__(self, bot: "custom.Bot") -> None:
        """Initialize a mapping for app command placeholders.

        Args:
            bot: Bot instance used to resolve application commands.

        """
        self.bot: custom.Bot = bot
        self._cache: TTLCache[str, str] = TTLCache(maxsize=32, ttl=timedelta(hours=1).seconds)

    @override
    def __getitem__(self, key: str) -> str:
        """Resolve a command placeholder to a command mention or name.

        Args:
            key: Command key, with subcommand separators encoded as ``__``.

        Returns:
            Command mention for slash commands, otherwise command name.

        Raises:
            KeyError: If no command matches the provided key.

        """
        key = key.replace("__", " ")
        if key in self._cache:
            return self._cache[key]
        if command := self.bot.get_application_command(key):  # pyright: ignore[reportUnknownVariableType]
            r = command.mention if isinstance(command, discord.SlashCommand) else command.name
            self._cache[key] = r
            return r
        raise KeyError(key)

    @override
    def __iter__(self) -> Iterator[str]:
        """Iterate command keys compatible with translation placeholders.

        Returns:
            An iterator of command keys using ``__`` separators.

        """
        for cmd in self.bot.walk_application_commands():  # pyright: ignore[reportUnknownVariableType]
            yield cmd.qualified_name.replace(" ", "__")

    @override
    def __len__(self) -> int:
        """Return the number of registered application commands.

        Returns:
            Count of application commands.

        """
        return len(self.bot._application_commands)  # pyright: ignore[reportUnknownArgumentType, reportPrivateUsage]  # noqa: SLF001


class EmojiMapping(Mapping[str, str]):
    def __init__(self, bot: "custom.Bot") -> None:
        """Initialize a mapping for application emoji placeholders.

        Args:
            bot: Bot instance used to resolve application emojis.

        """
        self.bot: custom.Bot = bot
        self._cache: TTLCache[str, str] = TTLCache(maxsize=32, ttl=timedelta(hours=1).seconds)

    @override
    def __getitem__(self, key: str) -> str:
        """Resolve an emoji placeholder to a mention string.

        Args:
            key: Emoji name.

        Returns:
            Mention string for the resolved emoji.

        Raises:
            KeyError: If no emoji with the given name exists.

        """
        if key in self._cache:
            return self._cache[key]
        try:
            emoji = next(emoji for emoji in self.bot.app_emojis if emoji.name == key).mention
            self._cache[key] = emoji
        except StopIteration as e:
            raise KeyError(key) from e
        else:
            return emoji

    @override
    def __iter__(self) -> Iterator[str]:
        """Iterate available emoji names.

        Returns:
            An iterator of application emoji names.

        """
        for emoji in self.bot.app_emojis:
            yield emoji.name

    @override
    def __len__(self) -> int:
        """Return the number of available application emojis.

        Returns:
            Count of application emojis.

        """
        return len(self.bot.app_emojis)


class TranslationCog(discord.Cog):
    def __init__(self, bot: "custom.Bot") -> None:
        """Initialize the translation cog.

        Args:
            bot: Bot instance used to populate translation placeholders.

        """
        self.bot: custom.Bot = bot

    @discord.Cog.listener(once=True)
    async def on_ready(self) -> None:
        """Populate global translation mappings when the bot becomes ready."""
        add_global_kv("commands", AppCommandMapping(self.bot))
        add_global_kv("emojis", EmojiMapping(self.bot))
        logger.success("Loaded translation cog")

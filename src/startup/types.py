# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

"""Type definitions for the startup system."""

from collections.abc import Awaitable
from typing import Protocol, TypedDict, overload, runtime_checkable

import discord
from quart import Quart

from src import custom


class ExtensionConfig(TypedDict, total=False):
    """Configuration dictionary for an extension.

    Note: This is a TypedDict with total=False to allow partial configs.
    The 'enabled' key is the only required field in practice.
    """

    enabled: bool
    translations: dict[str, object]
    # Extensions can have arbitrary additional config keys


@runtime_checkable
class SetupFunction(Protocol):
    """Protocol for extension setup functions that configure the bot.

    Extensions can define setup functions with different signatures.
    setup_func introspects the signature and passes only the required parameters.
    """

    @overload
    def __call__(self, *, bot: custom.Bot) -> None: ...

    @overload
    def __call__(self, *, config: ExtensionConfig) -> None: ...

    @overload
    def __call__(self, *, bot: custom.Bot, config: ExtensionConfig) -> None: ...

    def __call__(self, *, bot: custom.Bot | None = None, config: ExtensionConfig | None = None) -> None: ...


@runtime_checkable
class SetupWebserverFunction(Protocol):
    """Protocol for extension setup functions that configure the backend server.

    Extensions can define setup_webserver functions with different signatures.
    setup_func introspects the signature and passes only the required parameters.
    """

    @overload
    def __call__(self, *, app: Quart) -> None: ...

    @overload
    def __call__(self, *, bot: discord.Bot) -> None: ...

    @overload
    def __call__(self, *, config: ExtensionConfig) -> None: ...

    @overload
    def __call__(self, *, app: Quart, bot: discord.Bot) -> None: ...

    @overload
    def __call__(self, *, app: Quart, config: ExtensionConfig) -> None: ...

    @overload
    def __call__(self, *, bot: discord.Bot, config: ExtensionConfig) -> None: ...

    @overload
    def __call__(self, *, app: Quart, bot: discord.Bot, config: ExtensionConfig) -> None: ...

    def __call__(
        self, *, app: Quart | None = None, bot: discord.Bot | None = None, config: ExtensionConfig | None = None
    ) -> None: ...


@runtime_checkable
class StartupFunction(Protocol):
    """Protocol for extension startup functions that run during initialization.

    Extensions can define on_startup functions with different signatures.
    setup_func introspects the signature and passes only the required parameters.
    """

    @overload
    def __call__(self, *, app: Quart) -> Awaitable[None]: ...

    @overload
    def __call__(self, *, bot: discord.Bot) -> Awaitable[None]: ...

    @overload
    def __call__(self, *, config: ExtensionConfig) -> Awaitable[None]: ...

    @overload
    def __call__(self, *, app: Quart, bot: discord.Bot) -> Awaitable[None]: ...

    @overload
    def __call__(self, *, app: Quart, config: ExtensionConfig) -> Awaitable[None]: ...

    @overload
    def __call__(self, *, bot: discord.Bot, config: ExtensionConfig) -> Awaitable[None]: ...

    @overload
    def __call__(self, *, app: Quart, bot: discord.Bot, config: ExtensionConfig) -> Awaitable[None]: ...

    def __call__(
        self, *, app: Quart | None = None, bot: discord.Bot | None = None, config: ExtensionConfig | None = None
    ) -> Awaitable[None]: ...


SetupFunctionList = list[tuple[SetupFunction, ExtensionConfig]]
WebserverFunctionList = list[tuple[SetupWebserverFunction, ExtensionConfig]]
StartupFunctionList = list[tuple[StartupFunction, ExtensionConfig]]


__all__ = [
    "ExtensionConfig",
    "SetupFunction",
    "SetupFunctionList",
    "SetupWebserverFunction",
    "StartupFunction",
    "StartupFunctionList",
    "WebserverFunctionList",
]

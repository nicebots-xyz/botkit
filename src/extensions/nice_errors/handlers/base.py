# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

import contextlib
import logging
from abc import ABC, abstractmethod
from typing import Any, final, overload

import discord
import sentry_sdk

from src import custom
from src.i18n.classes import RawTranslation, apply_locale

logger = logging.getLogger("bot").getChild("nice_errors").getChild("handlers")


def _get_locale(ctx: custom.Context | discord.Interaction) -> str | None:
    locale: str | None = None
    if isinstance(ctx, custom.ApplicationContext):
        locale = ctx.locale or ctx.guild_locale
    elif isinstance(ctx, custom.ExtContext):
        if ctx.guild:
            locale = ctx.guild.preferred_locale
    elif isinstance(ctx, discord.Interaction):  # pyright: ignore[reportUnnecessaryIsInstance]
        locale = ctx.locale or ctx.guild_locale
    return locale


class BaseErrorHandler[E: Exception](ABC):
    def __init__(self, error_cls: type[E]) -> None:
        self.error_cls: type[E] = error_cls

    @abstractmethod
    async def __call__(
        self,
        error: E,
        ctx: custom.Context | discord.Interaction,
        sendargs: dict[str, Any],
        message: str,
        report: bool,
    ) -> "ErrorHandlerRType": ...

    @staticmethod
    def _get_locale(ctx: custom.Context | discord.Interaction) -> str | None:
        return _get_locale(ctx)


type ErrorHandlerRType = tuple[bool, bool, str, dict[str, Any]]  # handled, report, message, sendargs
type ErrorHandlerType[E: Exception] = BaseErrorHandler[E]
type ErrorHandlersType[E: Exception] = dict[
    type[E] | None,
    ErrorHandlerType[E],
]


@final
class ErrorHandlerManager:
    def __init__(self, error_handlers: ErrorHandlersType[Exception] | None = None) -> None:
        self.error_handlers: ErrorHandlersType[Exception] = error_handlers or {}

    def _get_handler(self, error: Exception) -> BaseErrorHandler[Exception] | None:
        if handler := self.error_handlers.get(type(error)):
            return handler
        with contextlib.suppress(StopIteration):
            return next(
                filter(lambda x: x[0] is not None and issubclass(type(error), x[0]), self.error_handlers.items())
            )[1]
        return None

    async def handle_error(
        self,
        error: Exception | discord.ApplicationCommandInvokeError,
        ctx: discord.Interaction | custom.Context,
        /,
        raw_translations: dict[str, RawTranslation],
        use_sentry_sdk: bool = False,
    ) -> None:
        original_error = error
        report: bool = True
        sendargs: dict[str, Any] = {
            "ephemeral": True,
        }
        message: str = ""
        translations = apply_locale(raw_translations, _get_locale(ctx))
        if isinstance(error, discord.ApplicationCommandInvokeError):
            original_error = error.original

        handler = self._get_handler(original_error) or self.error_handlers.get(None)
        if handler:
            handled, report, message, sendargs = await handler(
                original_error,
                ctx,
                sendargs,
                str(error),
                report,
            )
            if handled:
                return
        if report and use_sentry_sdk:
            out = sentry_sdk.capture_exception(error)
            message += f"\n\n-# {translations.reported_to_devs} - `{out}`"
        await ctx.respond(message, **sendargs)
        if report:
            raise error

    @overload
    def add_error_handler[E: Exception](self, error: None, handler: ErrorHandlerType[Exception]) -> None: ...

    @overload
    def add_error_handler[E: Exception](self, error: type[E], handler: ErrorHandlerType[E]) -> None: ...

    def add_error_handler[E: Exception](self, error: type[E] | None, handler: ErrorHandlerType[E | Exception]) -> None:
        logger.info(
            f"Adding error handler {handler.__class__.__qualname__} for {error.__qualname__ if error is not None else 'Generic'}"  # noqa: E501
        )
        self.error_handlers[error] = handler

    def remove_error_handler[E: Exception](self, error: type[E]) -> None:
        logger.info(f"Removing error handler {error.__qualname__}")
        del self.error_handlers[error]


__all__ = (
    "BaseErrorHandler",
    "ErrorHandlerManager",
    "ErrorHandlerRType",
    "ErrorHandlerType",
    "ErrorHandlersType",
)

# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz


from typing import Any, final, override

import discord

from src import custom
from src.i18n.classes import RawTranslation, apply_locale

from .base import BaseErrorHandler, ErrorHandlerRType


@final
class GenericErrorHandler(BaseErrorHandler[Exception]):
    def __init__(self, translations: dict[str, RawTranslation]) -> None:
        self.translations = translations
        super().__init__(Exception)

    @override
    async def __call__(
        self,
        error: Exception,
        ctx: custom.Context | discord.Interaction,
        sendargs: dict[str, Any],
        message: str,
        report: bool,
    ) -> ErrorHandlerRType:
        translations = apply_locale(self.translations, self._get_locale(ctx))

        message = translations.error_generic

        return False, report, message, sendargs

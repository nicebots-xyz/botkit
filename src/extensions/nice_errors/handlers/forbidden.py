# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz


from typing import Any, final, override

import discord

from src import custom
from src.i18n.classes import RawTranslation, apply_locale

from .base import BaseErrorHandler, ErrorHandlerRType


@final
class ForbiddenErrorHandler(BaseErrorHandler[discord.Forbidden]):
    def __init__(self, translations: dict[str, RawTranslation]) -> None:
        self.translations = translations
        super().__init__(discord.Forbidden)

    @override
    async def __call__(
        self,
        error: discord.Forbidden,
        ctx: custom.Context | discord.Interaction,
        sendargs: dict[str, Any],
        message: str,
        report: bool,
    ) -> ErrorHandlerRType:
        translations = apply_locale(self.translations, self._get_locale(ctx))

        message = translations.error_missing_permissions + f"\n`{error.args[0].split(':')[-1].strip()}`"

        return False, report, message, sendargs

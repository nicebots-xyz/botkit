# Copyright (c) NiceBots
# SPDX-License-Identifier: MIT

from typing import Any, final, override

import discord

from src import custom
from src.i18n.classes import RawTranslation, apply_locale
from src.utils.cooldown import CooldownExceeded

from .base import BaseErrorHandler, ErrorHandlerRType


@final
class CooldownErrorHandler(BaseErrorHandler[CooldownExceeded]):
    def __init__(self, translations: dict[str, RawTranslation]) -> None:
        self.translations = translations
        super().__init__(CooldownExceeded)

    @override
    async def __call__(
        self,
        error: CooldownExceeded,
        ctx: custom.Context | discord.Interaction,
        sendargs: dict[str, Any],
        message: str,
        report: bool,
    ) -> ErrorHandlerRType:
        translations = apply_locale(self.translations, self._get_locale(ctx))

        message = translations.error_cooldown_exceeded

        sendargs["ephemeral"] = True

        return False, False, message, sendargs

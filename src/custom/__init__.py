from typing_extensions import override
import discord
from src.i18n import apply_locale
from src.i18n.classes import ExtensionTranslation, TranslationWrapper
from typing import Any


class ApplicationContext(discord.ApplicationContext):
    def __init__(self, bot: discord.Bot, interaction: discord.Interaction):
        self.translations: TranslationWrapper = TranslationWrapper(
            {}, "en-US"
        )  # empty placeholder
        super().__init__(bot=bot, interaction=interaction)

    @override
    def __setattr__(self, key: Any, value: Any):
        if key == "command":
            if hasattr(value, "translations"):
                self.translations = apply_locale(
                    value.translations,
                    self.locale,
                )
        super().__setattr__(key, value)


class Bot(discord.Bot):
    def __init__(self, *args: Any, **options: Any):
        self.translations: list[ExtensionTranslation] = options.pop("translations", [])
        super().__init__(*args, **options)  # pyright: ignore[reportUnknownMemberType]

    @override
    async def get_application_context(
        self,
        interaction: discord.Interaction,
        cls: type[discord.ApplicationContext] = ApplicationContext,
    ):
        return await super().get_application_context(interaction, cls=cls)

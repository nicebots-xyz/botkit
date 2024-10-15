from typing import Any
from typing_extensions import override
from pydantic import BaseModel, Field

LOCALES = (
    "en-US",
    "en-GB",
    "bg",
    "zh-CN",
    "zh-TW",
    "hr",
    "cs",
    "da",
    "nl",
    "fi",
    "fr",
    "de",
    "el",
    "hi",
    "hu",
    "it",
    "ja",
    "ko",
    "lt",
    "no",
    "pl",
    "pt-BR",
    "ro",
    "ru",
    "es-ES",
    "es-419",
    "sv-SE",
    "th",
    "tr",
    "uk",
    "vi",
)
DEFAULT = "en-US"


class RawTranslation(BaseModel):
    en_US: str | None = Field(None, alias="en-US")
    en_GB: str | None = Field(None, alias="en-GB")
    bg: str | None = None
    zh_CN: str | None = Field(None, alias="zh-CN")
    zh_TW: str | None = Field(None, alias="zh-TW")
    hr: str | None = None
    cs: str | None = None
    da: str | None = None
    nl: str | None = None
    fi: str | None = None
    fr: str | None = None
    de: str | None = None
    el: str | None = None
    hi: str | None = None
    hu: str | None = None
    it: str | None = None
    ja: str | None = None
    ko: str | None = None
    lt: str | None = None
    no: str | None = None
    pl: str | None = None
    pt_BR: str | None = Field(None, alias="pt-BR")
    ro: str | None = None
    ru: str | None = None
    es_ES: str | None = Field(None, alias="es-ES")
    es_419: str | None = Field(None, alias="es-419")
    sv_SE: str | None = Field(None, alias="sv-SE")
    th: str | None = None
    tr: str | None = None
    uk: str | None = None
    vi: str | None = None

    class Config:
        populate_by_name = True


class Translation(BaseModel):
    def get_for_locale(self, locale: str) -> "TranslationWrapper":
        return apply_locale(self, locale)


class TranslationWrapper:
    def __init__(self, model: "Translatable", locale: str, default: str = DEFAULT):
        self._model = model
        self._default: str
        self.default = default
        self._locale: str
        self.locale = locale.replace("-", "_")

    def __getattr__(self, key: str) -> Any:
        if isinstance(self._model, dict):
            applicable = self._model.get(key)
            if not applicable:
                raise AttributeError
        else:
            applicable = getattr(self._model, key)
        if isinstance(applicable, RawTranslation):
            try:
                print(id(self._model))
                return getattr(applicable, self._locale)
            except AttributeError:
                return getattr(applicable, self._default)
        return apply_locale(applicable, self._locale)

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str | None) -> None:  # pyright: ignore[reportPropertyTypeMismatch]
        if value is None:
            value = self.default
        if value not in LOCALES:
            raise ValueError(f"Invalid locale {value}")
        self._locale = value

    @property
    def default(self) -> str:
        return self._default

    @default.setter
    def default(self, value: str) -> None:
        if value not in LOCALES:
            raise ValueError(f"Invalid locale {value}")
        self._default = value

    @override
    def __repr__(self) -> str:
        return repr(self._model)

    @override
    def __str__(self) -> str:
        return str(self._model)


Translatable = Translation | dict[str, Translation]


class NameDescriptionTranslation(Translation):
    name: RawTranslation | None = None
    description: RawTranslation | None = None


class CommandTranslation(NameDescriptionTranslation):
    strings: dict[str, RawTranslation] | None = None
    options: dict[str, NameDescriptionTranslation] | None = None


class Deg3CommandTranslation(CommandTranslation): ...


class Deg2CommandTranslation(CommandTranslation):
    commands: dict[str, Deg3CommandTranslation] | None = None


class Deg1CommandTranslation(CommandTranslation):
    commands: dict[str, Deg2CommandTranslation] | None = None


AnyCommandTranslation = (
    Deg1CommandTranslation | Deg2CommandTranslation | Deg3CommandTranslation
)


class ExtensionTranslation(Translation):
    commands: dict[str, Deg1CommandTranslation] | None = None
    strings: dict[str, RawTranslation] | None = None


def apply_locale(
    model: "Translatable | TranslationWrapper", locale: str, default: str = DEFAULT
) -> TranslationWrapper:
    if isinstance(model, TranslationWrapper):
        model.locale = locale
        model.default = default
        return model
    return TranslationWrapper(model, locale, default)

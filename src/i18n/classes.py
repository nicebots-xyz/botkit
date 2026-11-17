# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

import re
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from string import Formatter
from typing import Any, ClassVar, Self, cast, overload, override

from pydantic import BaseModel, RootModel, model_validator

from src.log import logger as main_logger

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

logger = main_logger.getChild("i18n")

# Matches `{namespace.key}` placeholders such as `{commands.help}` or `{emojis.check}`.
PLACEHOLDER = re.compile(r"\{(\w+)\.([\w-]+)\}")

# Namespaces that `i18n.apply()` registers, known before any bot exists so that stubs can be generated offline.
BUILTIN_NAMESPACES = frozenset({"commands", "emojis"})
# Separates the root of a replacement field from its attribute or index accesses, e.g. `{user.name}` or `{items[0]}`.
FIELD_ACCESS = re.compile(r"[.\[]")

GLOBAL_KV: dict[str, Mapping[str, str]] = {}
_CACHE: dict[tuple[int, str], tuple[object, Any]] = {}


@dataclass(frozen=True, slots=True)
class FormatFields:
    """The arguments a string expects from ``str.format``.

    Attributes:
        positional: Number of positional arguments, from ``{}`` or ``{0}`` fields.
        named: Names of the keyword arguments.

    """

    positional: int = 0
    named: tuple[str, ...] = ()

    def __bool__(self) -> bool:
        return bool(self.positional or self.named)


def format_fields(text: str, namespaces: frozenset[str] | None = None) -> FormatFields | None:
    """Find the ``str.format`` arguments of a string, ignoring ``{namespace.key}`` placeholders.

    Args:
        text: The string to inspect.
        namespaces: Placeholder namespaces resolved by localization, the builtin and registered ones if None.

    Returns:
        The arguments, None if the string is not a valid format string.

    """
    if namespaces is None:
        namespaces = BUILTIN_NAMESPACES | GLOBAL_KV.keys()
    positional = 0
    named: dict[str, None] = {}
    pending = [text]
    try:
        while pending:
            for _, field, spec, _ in Formatter().parse(pending.pop()):
                if field is None:
                    continue
                root = FIELD_ACCESS.split(field, maxsplit=1)[0]
                if root in namespaces and root != field:
                    continue
                if spec:  # specs can hold nested fields, e.g. `{value:{width}}`
                    pending.append(spec)
                if not root:
                    positional += 1
                elif root.isdigit():
                    positional = max(positional, int(root) + 1)
                else:
                    named[root] = None
    except ValueError:
        return None
    return FormatFields(positional, tuple(named))


def add_global_kv(key: str, values: Mapping[str, str]) -> None:
    """Register a placeholder namespace resolved in every translation string.

    Args:
        key: Namespace used in placeholders, e.g. ``commands`` for ``{commands.help}``.
        values: Mapping from placeholder keys to their replacement text.

    """
    GLOBAL_KV[key] = values
    clear_cache()


def clear_cache() -> None:
    """Forget every localized view so that placeholders are resolved again on next access."""
    _CACHE.clear()


def _replace(match: re.Match[str]) -> str:
    """Resolve one placeholder match, leaving unknown namespaces and keys untouched.

    Args:
        match: A match of ``PLACEHOLDER``.

    Returns:
        The replacement text, or the original placeholder.

    """
    return GLOBAL_KV.get(match[1], {}).get(match[2], match[0])


def missing_placeholders() -> set[str]:
    """Find placeholders of a registered namespace whose key does not exist.

    Returns:
        The unresolvable placeholders, e.g. ``{"{commands.hlep}"}``.

    """
    return {
        match[0]
        for raw in RawTranslation.REGISTRY
        for text in raw.root.values()
        for match in PLACEHOLDER.finditer(text)
        if match[1] in GLOBAL_KV and match[2] not in GLOBAL_KV[match[1]]
    }


def check_placeholders() -> None:
    """Ensure every ``{namespace.key}`` placeholder of a registered namespace can be resolved.

    Raises:
        KeyError: If some placeholders reference keys that do not exist.

    """
    if missing := missing_placeholders():
        message = "Translations reference unknown keys: " + ", ".join(sorted(missing))
        logger.error(message)
        raise KeyError(message)


class RawTranslation(RootModel[dict[str, str]]):
    """A single translatable string, mapping locales to their text."""

    REGISTRY: ClassVar[list["RawTranslation"]] = []

    @model_validator(mode="after")
    def _check_locales(self) -> Self:
        if unknown := self.root.keys() - set(LOCALES):
            raise ValueError(f"Unknown locales {sorted(unknown)}")
        if DEFAULT not in self.root:
            raise ValueError(f"Missing the {DEFAULT} translation")
        self._check_fields()
        return self

    def _check_fields(self) -> None:
        """Ensure no locale expects ``str.format`` arguments that the default locale does not.

        Code formats a string with the arguments of its default text, so any other one would fail at runtime.

        Raises:
            ValueError: If a locale uses a positional or keyword argument the default locale does not.

        """
        default = format_fields(self.root[DEFAULT])
        if default is None:
            return
        for locale, text in self.root.items():
            fields = format_fields(text)
            if fields is None:
                raise ValueError(f"The {locale} translation is not a valid format string: {text!r}")
            if extra := [f"{{{name}}}" for name in fields.named if name not in default.named]:
                raise ValueError(f"The {locale} translation uses {', '.join(extra)}, unknown in {DEFAULT}")
            if (count := fields.positional) > default.positional:
                raise ValueError(f"The {locale} translation uses {count} positional fields, more than {DEFAULT}")

    @override
    def model_post_init(self, context: Any, /) -> None:
        RawTranslation.REGISTRY.append(self)

    def get_for_locale(self, locale: str | None) -> str:
        """Get the text for a locale, falling back to the default locale.

        Args:
            locale: The locale to get the text for.

        Returns:
            The text with its global placeholders resolved.

        """
        return apply_locale(self, locale)


class Translation(BaseModel):
    def get_for_locale(self, locale: str | None) -> "Strings":
        """Localize this translation.

        Args:
            locale: The locale to localize for.

        Returns:
            The localized view of this translation.

        """
        return apply_locale(self, locale)


class Strings(Mapping[str, Any]):
    """A translation localized for one locale, readable by attribute or by key."""

    def __init__(self, values: Mapping[str, Any]) -> None:
        self.__dict__.update(values)

    @override
    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __getattr__(self, key: str) -> Any:
        raise AttributeError(f"No translation for {key!r}")

    @override
    def __iter__(self) -> Iterator[str]:
        return iter(self.__dict__)

    @override
    def __len__(self) -> int:
        return len(self.__dict__)

    @override
    def __repr__(self) -> str:
        return f"Strings({self.__dict__!r})"


def typed[T](strings: Strings, protocol: type[T]) -> T:  # noqa: ARG001
    """Type a localized view with the protocol that ``pdm run i18n-stubs`` generated for it.

    Args:
        strings: The localized view, e.g. ``ctx.translations``.
        protocol: The generated protocol, e.g. ``PingCommandStrings``.

    Returns:
        The same view, typed with the protocol.

    """
    return cast("T", strings)


type Translatable = Translation | Mapping[str, RawTranslation]


def _localize(value: object, locale: str) -> Any:
    """Recursively turn a translation tree into plain values for one locale.

    Args:
        value: A translation, a mapping or list of them, or any plain value.
        locale: The locale to localize for.

    Returns:
        Strings for models and mappings, lists for lists, text for raw translations, other values as is.

    """
    if isinstance(value, RawTranslation):
        return PLACEHOLDER.sub(_replace, value.root.get(locale) or value.root[DEFAULT])
    if isinstance(value, BaseModel):
        value = dict(value)
    if isinstance(value, Mapping):
        items: Mapping[str, object] = value  # pyright: ignore[reportUnknownVariableType]
        return Strings({key: _localize(item, locale) for key, item in items.items()})
    if isinstance(value, list):
        elements: list[object] = value  # pyright: ignore[reportUnknownVariableType]
        return [_localize(item, locale) for item in elements]
    return value


@overload
def apply_locale(model: RawTranslation, locale: str | None) -> str: ...
@overload
def apply_locale(model: Translatable, locale: str | None) -> Strings: ...


def apply_locale(model: RawTranslation | Translatable, locale: str | None) -> str | Strings:
    """Localize a translation, computing it once per locale.

    The model must be long-lived, as it is kept in the cache.

    Args:
        model: The translation to localize.
        locale: The locale to localize for, the default locale if None.

    Returns:
        The localized text for a raw translation, its localized view otherwise.

    """
    locale = locale or DEFAULT
    key = (id(model), locale)
    if key not in _CACHE:
        _CACHE[key] = (model, _localize(model, locale))
    return _CACHE[key][1]


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


AnyCommandTranslation = Deg1CommandTranslation | Deg2CommandTranslation | Deg3CommandTranslation


class ExtensionTranslation(Translation):
    commands: dict[str, Deg1CommandTranslation] | None = None
    strings: dict[str, RawTranslation] | None = None

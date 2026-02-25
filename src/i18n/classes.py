# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

from collections.abc import Generator, Iterator, Mapping, Sequence
from typing import Any, ClassVar, Self, cast, overload, override

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


class _Placeholder:
    def __init__(self, key: str) -> None:
        """Initialize a placeholder key path.

        Args:
            key: Placeholder key path used for deferred formatting.

        """
        self._key: str = key

    def __getattr__(self, attr: str) -> "_Placeholder":
        """Extend the placeholder path using attribute-style access.

        Args:
            attr: Attribute name to append to the key path.

        Returns:
            A new placeholder with the appended key path.

        """
        return _Placeholder(f"{self._key}.{attr}")

    def __getitem__(self, item: str | int) -> "_Placeholder":
        """Extend the placeholder path using index-style access.

        Args:
            item: Index or key to append to the key path.

        Returns:
            A new placeholder with the appended indexed path.

        """
        return _Placeholder(f"{self._key}[{item}]")

    @override
    def __format__(self, spec: str) -> str:
        """Render a placeholder token that preserves unresolved values.

        Args:
            spec: Optional format specifier for the placeholder.

        Returns:
            A format token string for unresolved placeholders.

        """
        if spec:
            return "{" + self._key + ":" + spec + "}"
        return "{" + self._key + "}"


class AttrDict[K: str, V](Mapping[K, V]):
    def __init__(self, underlying: Mapping[K, V]) -> None:
        """Wrap a mapping to support both key and attribute access.

        Args:
            underlying: Mapping to expose through this wrapper.

        """
        self.underlying: Mapping[K, V] = underlying

    @override
    def __len__(self) -> int:
        """Return the number of keys in the wrapped mapping.

        Returns:
            The mapping size.

        """
        return len(self.underlying)

    @override
    def __iter__(self) -> Iterator[K]:
        """Iterate over keys in the wrapped mapping.

        Returns:
            An iterator of mapping keys.

        """
        return iter(self.underlying)

    @override
    def __getitem__(self, key: K) -> V:
        """Retrieve a value by key from the wrapped mapping.

        Args:
            key: Key to resolve.

        Returns:
            Value associated with the key.

        """
        return self.underlying[key]

    def __getattr__(self, key: K) -> V:
        """Retrieve a value as an attribute.

        Args:
            key: Attribute name mapped to a dictionary key.

        Returns:
            Value associated with the key.

        Raises:
            AttributeError: If the key is not present in the mapping.

        """
        try:
            return self.__getitem__(key)
        except KeyError as e:
            raise AttributeError(key) from e


class LazyPartialDict[V: Mapping[str, str]](dict[str, AttrDict[str, str] | _Placeholder]):
    def __init__(self, data: dict[str, V]) -> None:
        """Initialize deferred formatting data.

        Args:
            data: Source values used when placeholders are available.

        """
        super().__init__()
        self._data: dict[str, V] = data

    def __missing__(self, key: str) -> AttrDict[str, str] | _Placeholder:
        """Resolve missing keys for partial formatting.

        Args:
            key: Missing key requested by ``str.format_map``.

        Returns:
            Wrapped mapping if key exists, otherwise a placeholder token.

        """
        if key in self._data:
            return AttrDict(self._data[key])
        return _Placeholder(key)


def add_global_kv(key: str, values: Mapping[str, str]) -> None:
    """Add a key-value mapping to the global translation dictionary.

    This function updates the global translation dictionary with a given
    key-value pair. The key will map to a dictionary containing additional
    key-value mappings that can be used for various translation or
    application-specific purposes.

    Args:
        key: The key to be added to the global translation dictionary.
        values: A dictionary containing key-value mappings to associate with the
        given key in the global translation dictionary.

    """
    TranslationWrapper.GLOBAL_KV[key] = values


def partial_fmt(template: str, data: dict[str, Mapping[str, str]]) -> str:
    """Format a template string with partial data, leaving missing keys intact.

    Args:
        template: A format string with `{key.attr}` style placeholders.
        data: A dict mapping top-level keys to dicts of their attributes.

    Returns:
        The template with available keys resolved, missing keys left as-is.

    """
    return template.format_map(LazyPartialDict(data))


class RawTranslation(BaseModel):
    en_US: str | None = Field(None, alias="en-US")  # noqa: N815
    en_GB: str | None = Field(None, alias="en-GB")  # noqa: N815
    bg: str | None = None
    zh_CN: str | None = Field(None, alias="zh-CN")  # noqa: N815
    zh_TW: str | None = Field(None, alias="zh-TW")  # noqa: N815
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
    pt_BR: str | None = Field(None, alias="pt-BR")  # noqa: N815
    ro: str | None = None
    ru: str | None = None
    es_ES: str | None = Field(None, alias="es-ES")  # noqa: N815
    es_419: str | None = Field(None, alias="es-419")
    sv_SE: str | None = Field(None, alias="sv-SE")  # noqa: N815
    th: str | None = None
    tr: str | None = None
    uk: str | None = None
    vi: str | None = None

    class Config:
        populate_by_name: bool = True

    def get_for_locale(self, locale: str) -> str | None:
        """Get translation for a specific locale, falling back to the field default."""
        return self.model_dump(by_alias=False).get(locale.replace("-", "_"))


class Translation(BaseModel):
    def get_for_locale(self, locale: str) -> "TranslationWrapper[Self]":
        return apply_locale(self, locale)


Translatable = Translation | dict[str, RawTranslation]

type WrappedInput[V: Translatable] = None | str | int | float | bool | RawTranslation | Sequence["WrappedInput[V]"] | V
type WrappedValue[V: Translatable] = None | str | int | float | bool | list["WrappedValue[V]"] | "TranslationWrapper[V]"


class TranslationWrapper[T: Translatable]:
    def __init__(self, model: T, locale: str, default: str = DEFAULT) -> None:
        self._model: T = model
        self._default: str
        self.default = default.replace("-", "_")
        self._locale: str
        self.locale = locale.replace("-", "_")

    GLOBAL_KV: ClassVar[dict[str, Mapping[str, str]]] = {}

    @overload
    def _wrap_value(self, value: None) -> None: ...
    @overload
    def _wrap_value(self, value: str | float | bool) -> str | int | float | bool: ...
    @overload
    def _wrap_value(self, value: RawTranslation) -> str | None: ...
    @overload
    def _wrap_value[V: Translatable](self, value: Sequence[WrappedInput[V]]) -> list[WrappedValue[V]]: ...
    @overload
    def _wrap_value[V: Translatable](self, value: V) -> "TranslationWrapper[V]": ...

    def _wrap_value[V: Translatable](
        self, value: None | str | float | bool | RawTranslation | Sequence[WrappedInput[V]] | V
    ) -> Any:
        """Consistently wrap values in TranslationWrapper if needed."""
        if value is None:
            return None
        if isinstance(value, str | int | float | bool):
            return value
        if isinstance(value, RawTranslation):
            r = value.get_for_locale(self._locale) or value.get_for_locale(self._default)
            return partial_fmt(r, self.GLOBAL_KV) if r else None
        if isinstance(value, Sequence):
            return [self._wrap_value(item) for item in value]

        return apply_locale(value, self._locale)

    def __getattr__(self, key: str) -> Any:
        if isinstance(self._model, dict):
            if key not in self._model:
                raise AttributeError(f'Key "{key}" not found in {self._model}')
            value: WrappedInput[Translatable] = self._model[key]
        else:
            value = getattr(self._model, key)
        return self._wrap_value(value)

    def __getitem__(self, item: object) -> Any:
        if not isinstance(item, str):
            raise TypeError(f"Key must be a string, not {type(item).__name__}")
        return self.__getattr__(item)

    def keys(self) -> Generator[str, None, None]:
        if not isinstance(self._model, dict):
            raise TypeError(f"Cannot get keys from {type(self._model).__name__}")
        yield from self._model.keys()

    def items(self) -> Generator[tuple[str, WrappedValue[Translatable]], None, None]:
        if isinstance(self._model, dict):
            for key, value in self._model.items():
                yield key, self._wrap_value(value)
        else:
            for key in self.keys():
                yield key, self._wrap_value(cast("WrappedInput[Translatable]", getattr(self._model, key)))

    def values(self) -> Generator[WrappedValue[Translatable], None, None]:
        if isinstance(self._model, dict):
            for value in self._model.values():
                yield self._wrap_value(value)
        else:
            for key in self.keys():
                yield self._wrap_value(cast("WrappedInput[Translatable]", getattr(self._model, key)))

    def __iter__(self) -> Iterator[WrappedValue[Translatable]]:
        yield from self.keys()

    def __len__(self) -> int:
        if isinstance(self._model, dict):
            return len(self._model)
        return len(self._model.__dict__)

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str | None) -> None:  # pyright: ignore[reportPropertyTypeMismatch]
        if value is None:
            value = self.default
        if value.replace("_", "-") not in LOCALES:
            raise ValueError(f"Invalid locale {value}")
        self._locale = value

    @property
    def default(self) -> str:
        return self._default

    @default.setter
    def default(self, value: str) -> None:
        if value.replace("_", "-") not in LOCALES:
            raise ValueError(f"Invalid locale {value}")
        self._default = value

    @override
    def __repr__(self) -> str:
        return f"TranslationWrapper({self._model!r}, locale={self._locale!r}, default={self._default!r})"

    @override
    def __str__(self) -> str:
        return str(self._model)


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


def apply_locale[T: "Translatable"](
    model: T | TranslationWrapper[T],
    locale: str | None,
    default: str | None = DEFAULT,
) -> TranslationWrapper[T]:
    default = default if default is not None else DEFAULT
    if locale is None:
        locale = DEFAULT
    if isinstance(model, TranslationWrapper):
        model.locale = locale
        model.default = default
        return model
    return TranslationWrapper(model, locale, default)

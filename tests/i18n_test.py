# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

import asyncio
from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

import discord
import pytest
import yaml
from pydantic import ValidationError

from scripts.i18n_stubs.__main__ import render, stubs
from src import custom
from src.i18n import classes, utils
from src.i18n.classes import (
    ExtensionTranslation,
    FormatFields,
    RawTranslation,
    add_global_kv,
    apply_locale,
    check_placeholders,
    format_fields,
)
from src.i18n.utils import CommandMapping, find_translation_files, load_translation


@pytest.fixture(autouse=True)
def clean_globals() -> Iterator[None]:
    yield
    classes.GLOBAL_KV.clear()
    classes.clear_cache()


def test_folder_matches_single_file(tmp_path: Path) -> None:
    single = tmp_path / "translations.yml"
    single.write_text(
        yaml.safe_dump(
            {
                "commands": {"ping": {"strings": {"response": {"en-US": "Pong"}}}},
                "strings": {"hello": {"en-US": "Hello"}},
            }
        ),
        encoding="utf-8",
    )
    folder = tmp_path / "translations"
    (folder / "commands").mkdir(parents=True)
    (folder / "commands" / "ping.yml").write_text("strings:\n  response:\n    en-US: Pong\n", encoding="utf-8")
    (folder / "strings.yaml").write_text("hello:\n  en-US: Hello\n", encoding="utf-8")
    (folder / "notes.txt").write_text("ignored", encoding="utf-8")

    assert load_translation(folder) == load_translation(single)


def _write(path: Path, data: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def test_find_translation_files_puts_the_extension_first(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    extension = tmp_path / "extensions" / "premium"
    extension.mkdir(parents=True)
    central = tmp_path / "translations"
    central.mkdir()
    monkeypatch.setattr(utils, "TRANSLATIONS", central)

    assert find_translation_files(extension, "premium") == []
    override = _write(central / "premium.yml", {})
    assert find_translation_files(extension, "premium") == [override]
    own = _write(extension / "translations.yaml", {})
    assert find_translation_files(extension, "premium") == [own, override]


def test_overrides_are_merged_per_locale(tmp_path: Path) -> None:
    base = _write(
        tmp_path / "base.yml",
        {
            "commands": {
                "subscribe": {
                    "description": {"en-US": "Subscribe", "fr": "S'abonner"},
                    "strings": {
                        "name": {"en-US": "Premium", "fr": "Premium"},
                        "pitch": {"en-US": "Unlock {feature}", "fr": "Débloquez {feature}"},
                    },
                }
            },
            "strings": {"cooldown": {"en-US": "Wait {time}s"}},
        },
    )
    override = _write(
        tmp_path / "override.yml",
        {
            "commands": {
                "subscribe": {
                    "strings": {
                        "name": {"en-US": "ImageTools Pro", "de": "ImageTools Pro"},
                        "pitch": {"en-US": "Unlock everything"},
                        "level_1_name": {"en-US": "Basic"},
                    },
                }
            },
        },
    )

    translation = load_translation(base, override)
    assert translation.commands
    command = translation.commands["subscribe"]
    assert command.description == RawTranslation({"en-US": "Subscribe", "fr": "S'abonner"})
    assert command.strings
    assert {key: raw.root for key, raw in command.strings.items()} == {
        "name": {"en-US": "ImageTools Pro", "fr": "Premium", "de": "ImageTools Pro"},
        "pitch": {"en-US": "Unlock everything", "fr": "Débloquez {feature}"},
        "level_1_name": {"en-US": "Basic"},
    }
    assert translation.strings == {"cooldown": RawTranslation({"en-US": "Wait {time}s"})}


def test_overrides_may_complete_a_base_locale(tmp_path: Path) -> None:
    base = _write(tmp_path / "base.yml", {"strings": {"hello": {"en-US": "Hello {name}"}}})
    override = _write(tmp_path / "override.yml", {"strings": {"hello": {"fr": "Bonjour {name}"}}})

    assert load_translation(base, override).strings == {
        "hello": RawTranslation({"en-US": "Hello {name}", "fr": "Bonjour {name}"})
    }


@pytest.mark.parametrize(
    "override",
    [
        {"en-US": "Wait {time}s, {user}"},
        {"fr": "Attendez {duration}s"},
        {"en-US": "Wait {}s"},
        {"de": "Warte {0}s"},
    ],
)
def test_overrides_keep_the_base_format_fields(tmp_path: Path, override: dict[str, str]) -> None:
    base = _write(tmp_path / "base.yml", {"strings": {"cooldown": {"en-US": "Wait {time}s"}}})
    overrides = _write(tmp_path / "override.yml", {"strings": {"cooldown": override}})

    pattern = r"^strings\.cooldown: The (en-US|fr|de) translation uses .+ the en-US text of .+base\.yml$"
    with pytest.raises(ValueError, match=pattern):
        load_translation(base, overrides)


def test_strings_added_by_overrides_check_their_own_fields(tmp_path: Path) -> None:
    base = _write(tmp_path / "base.yml", {"strings": {}})
    override = _write(tmp_path / "override.yml", {"strings": {"extra": {"en-US": "{a}", "fr": "{b}"}}})

    with pytest.raises(ValueError, match=r"^strings\.extra: The fr translation uses \{b\}, unknown in en-US$"):
        load_translation(base, override)


def test_load_translation_requires_a_path() -> None:
    with pytest.raises(ValueError, match="At least one"):
        load_translation()


def test_folder_skips_folders_without_yaml(tmp_path: Path) -> None:
    folder = tmp_path / "translations"
    (folder / "__pycache__").mkdir(parents=True)
    (folder / "__pycache__" / "strings.cpython-312.pyc").write_bytes(b"")
    (folder / "strings.yml").write_text("hello:\n  en-US: Hello\n", encoding="utf-8")

    assert load_translation(folder) == ExtensionTranslation.model_validate({"strings": {"hello": {"en-US": "Hello"}}})


def test_find_translation_files_needs_a_folder_at_the_folder_path(tmp_path: Path) -> None:
    """A file named like the translations folder, such as a stub package's module, is not a translation."""
    (tmp_path / "translations").write_text("# not YAML", encoding="utf-8")

    assert find_translation_files(tmp_path, "no_such_extension") == []


def _classes_by_module(source: Path) -> dict[str, set[str]]:
    root = source.parent.resolve()
    return {
        str(path.relative_to(root)): {
            line.split("(")[0].removeprefix("class ") for line in code.splitlines() if line.startswith("class ")
        }
        for path, code in stubs(source).items()
    }


def test_stubs_of_a_file_sit_next_to_it(tmp_path: Path) -> None:
    source = tmp_path / "translations.yml"
    _write(
        source,
        {"commands": {"ping": {"strings": {"pong": {"en-US": "Pong"}}}}, "strings": {"hello": {"en-US": "Hello"}}},
    )

    assert _classes_by_module(source) == {"translations.py": {"ExtensionStrings", "PingCommandStrings"}}


def test_stubs_of_a_folder_follow_its_files(tmp_path: Path) -> None:
    """Each class goes to the module of the deepest file or folder holding its strings."""
    source = tmp_path / "translations"
    _write(source / "strings.yml", {"hello": {"en-US": "Hello"}})
    _write(source / "commands" / "ping.yml", {"strings": {"pong": {"en-US": "Pong"}}})
    _write(source / "commands" / "admin" / "commands" / "kick.yml", {"strings": {"done": {"en-US": "Kicked {user}"}}})
    _write(source / "commands" / "meow" / "strings" / "purr.yml", {"en-US": "Purr"})
    _write(source / "commands" / "meow" / "strings" / "hiss.yml", {"en-US": "Hiss"})

    assert _classes_by_module(source) == {
        "translations/__init__.py": set(),
        "translations/commands/__init__.py": set(),
        "translations/commands/admin/__init__.py": set(),
        "translations/commands/admin/commands/__init__.py": set(),
        "translations/commands/meow/__init__.py": set(),
        "translations/strings.py": {"ExtensionStrings"},
        "translations/commands/ping.py": {"PingCommandStrings"},
        "translations/commands/admin/commands/kick.py": {"AdminKickCommandDone", "AdminKickCommandStrings"},
        "translations/commands/meow/strings/__init__.py": {"MeowCommandStrings"},
    }


def test_raw_translation_requires_known_locales_and_default() -> None:
    with pytest.raises(ValidationError, match="Missing the en-US translation"):
        RawTranslation({"fr": "Bonjour"})
    with pytest.raises(ValidationError, match="Unknown locales"):
        RawTranslation({"en-US": "Hello", "xx": "?"})


def test_apply_locale_falls_back_and_caches() -> None:
    strings = {"hello": RawTranslation({"en-US": "Hello", "fr": "Bonjour"})}

    french = apply_locale(strings, "fr")
    assert french.hello == "Bonjour"
    assert french["hello"] == "Bonjour"
    assert apply_locale(strings, "de").hello == "Hello"
    assert apply_locale(strings, None).hello == "Hello"
    assert apply_locale(strings, "fr") is french
    assert repr(french) == "Strings({'hello': 'Bonjour'})"
    with pytest.raises(AttributeError):
        _ = french.missing


def test_placeholders_are_resolved_once_registered() -> None:
    raw = RawTranslation({"en-US": "Try {commands.help} {emojis.ok} in {latency:.1f}ms, {user.name}"})
    assert raw.get_for_locale("en-US") == "Try {commands.help} {emojis.ok} in {latency:.1f}ms, {user.name}"

    add_global_kv("commands", {"help": "</help:1>"})
    assert raw.get_for_locale("en-US") == "Try </help:1> {emojis.ok} in {latency:.1f}ms, {user.name}"


def test_check_placeholders_reports_unknown_keys() -> None:
    _ = RawTranslation({"en-US": "{test_ns.present} {test_ns.absent}"})
    add_global_kv("test_ns", {"present": "here"})

    with pytest.raises(KeyError, match=r"\{test_ns\.absent\}"):
        check_placeholders()
    add_global_kv("test_ns", {"present": "here", "absent": "here too"})
    check_placeholders()


async def _bot_with_group() -> discord.Bot:
    bot = discord.Bot()
    group = bot.create_group("admin", "Admin commands")

    @group.command()
    async def kick(_ctx: discord.ApplicationContext) -> None: ...

    return bot


def test_command_mapping_knows_unsynced_commands() -> None:
    mapping = CommandMapping(asyncio.run(_bot_with_group()))  # pyright: ignore[reportArgumentType]
    assert set(mapping) == {"admin", "admin__kick"}
    assert "admin__kick" in mapping
    assert "ban" not in mapping
    with pytest.raises(KeyError):
        _ = mapping["admin__kick"]  # no id to mention it with before the sync


def test_render_stubs() -> None:
    translation = ExtensionTranslation.model_validate(
        {
            "strings": {"hello": {"en-US": "Hello"}},
            "commands": {
                "my-group": {"commands": {"sub_cmd": {"strings": {"done": {"en-US": "Done"}}}}},
                "plain": {"name": {"en-US": "plain"}},
            },
        }
    )
    stub = render(translation)
    assert stub is not None
    assert "class ExtensionStrings(Protocol):\n    @property\n    def hello(self) -> str: ..." in stub
    assert "class MyGroupSubCmdCommandStrings(Protocol):\n    @property\n    def done(self) -> str: ..." in stub
    assert "Plain" not in stub
    assert render(ExtensionTranslation()) is None


def test_render_stubs_for_context_menu_commands() -> None:
    translation = ExtensionTranslation.model_validate(
        {"commands": {"Extract text (OCR)": {"strings": {"done": {"en-US": "Done in {seconds}s"}}}}},
    )
    stub = render(translation)
    assert stub is not None
    assert "class ExtractTextOCRCommandDone(str):" in stub
    assert "class ExtractTextOCRCommandStrings(Protocol):" in stub


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Hello", FormatFields()),
        ("{{literal}} braces", FormatFields()),
        ("Pong! {latency}ms, see {commands.help} {emojis.check}", FormatFields(named=("latency",))),
        ("{user.name} has {count:,} {user[0]}", FormatFields(named=("user", "count"))),
        ("{} and {}", FormatFields(positional=2)),
        ("{1} before {0}", FormatFields(positional=2)),
        ("{value:>{width}}", FormatFields(named=("value", "width"))),
        ("{commands}", FormatFields(named=("commands",))),
        ("Unclosed {", None),
    ],
)
def test_format_fields(text: str, expected: FormatFields | None) -> None:
    assert format_fields(text) == expected


def test_raw_translation_rejects_unknown_format_fields() -> None:
    RawTranslation({"en-US": "Page {current} of {total}", "fr": "Page {current}", "de": "Seite"})
    with pytest.raises(ValidationError, match=r"fr translation uses \{totl\}, unknown in en-US"):
        RawTranslation({"en-US": "Page {current} of {total}", "fr": "Page {current} sur {totl}"})
    with pytest.raises(ValidationError, match="fr translation uses 2 positional fields"):
        RawTranslation({"en-US": "{} items", "fr": "{} sur {}"})
    with pytest.raises(ValidationError, match="fr translation is not a valid format string"):
        RawTranslation({"en-US": "Page {current}", "fr": "Page {current"})


def test_render_types_format_arguments() -> None:
    translation = ExtensionTranslation.model_validate(
        {
            "strings": {"page": {"en-US": "Page {current} of {total}, see {commands.help}"}},
            "commands": {"ping": {"strings": {"pair": {"en-US": "{} and {}"}, "plain": {"en-US": "Pong"}}}},
        }
    )
    stub = render(translation)
    assert stub is not None
    assert "# pyright: reportIncompatibleMethodOverride=false" in stub
    assert "from typing import Protocol, final, override" in stub
    assert "class ExtensionPage(str):" in stub
    assert "def format(self, *, current: object, total: object) -> str: ..." in stub
    assert "def page(self) -> ExtensionPage: ..." in stub
    assert "def format(self, arg0: object, arg1: object, /) -> str: ..." in stub
    assert "def pair(self) -> PingCommandPair: ..." in stub
    assert "def plain(self) -> str: ..." in stub


def test_render_rejects_colliding_class_names() -> None:
    translation = ExtensionTranslation.model_validate(
        {"strings": {"a_b": {"en-US": "{x}"}, "aB": {"en-US": "{y}"}}},
    )
    with pytest.raises(ValueError, match="ExtensionAB"):
        render(translation)


@pytest.mark.parametrize("key", ["my-key", "class", "2fast"])
def test_render_rejects_invalid_identifiers(key: str) -> None:
    translation = ExtensionTranslation.model_validate({"strings": {key: {"en-US": "Text"}}})
    with pytest.raises(ValueError, match="not a valid Python identifier"):
        render(translation)


class _GreetStrings(Protocol):
    @property
    def hello(self) -> str: ...


class _Greet(discord.Cog):
    @discord.slash_command()
    async def greet(self, ctx: custom.ApplicationContext[_GreetStrings], name: str) -> None:
        await ctx.respond(ctx.translations.hello + name)


async def _bot_with_greet() -> discord.Bot:
    bot = discord.Bot()
    bot.add_cog(_Greet())
    return bot


def test_typed_context_is_a_plain_class_at_runtime() -> None:
    assert custom.ApplicationContext[_GreetStrings] is custom.ApplicationContext
    (command,) = asyncio.run(_bot_with_greet()).pending_application_commands  # pyright: ignore[reportUnknownVariableType]
    assert [option.name for option in command.options] == ["name"]  # pyright: ignore[reportUnknownVariableType]

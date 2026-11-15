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

from scripts.i18n_stubs.__main__ import render
from src import custom
from src.i18n import classes
from src.i18n.classes import (
    ExtensionTranslation,
    RawTranslation,
    add_global_kv,
    apply_locale,
    check_placeholders,
)
from src.i18n.utils import CommandMapping, load_translation


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

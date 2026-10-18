# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

import asyncio
from types import SimpleNamespace
from typing import Any, cast

import aiocache
import pytest
from discord.ext import commands

from src import custom
from src.utils.cooldown import BucketType, CooldownExceeded, cooldown


def _target_key(kwargs: dict[str, Any]) -> str | None:  # pyright: ignore[reportExplicitAny]
    target = kwargs.get("target")
    return None if target is None else str(target)


class _Cog(commands.Cog):
    def __init__(self) -> None:
        self.calls: int = 0
        super().__init__()

    @cooldown("pair", limit=1, per=60, bucket_type=BucketType.USER, extra_key=_target_key)
    async def pair(self, ctx: custom.Context, *, target: int | None = None) -> None:  # noqa: ARG002
        self.calls += 1


def _ctx(author_id: int) -> custom.Context:
    bot = SimpleNamespace(botkit_cache=aiocache.SimpleMemoryCache())
    ctx = SimpleNamespace(bot=bot, author=SimpleNamespace(id=author_id), guild=None, channel=None)
    return cast("custom.Context", cast("object", ctx))


def test_extra_key_scopes_cooldown_per_pair() -> None:
    """Test that the extra key gives each (actor, target) pair its own cooldown."""
    cog = _Cog()
    ctx = _ctx(1)

    async def run() -> None:
        await cog.pair(ctx, target=10)
        await cog.pair(ctx, target=20)
        with pytest.raises(CooldownExceeded):
            await cog.pair(ctx, target=10)

    asyncio.run(run())
    assert cog.calls == 2


def test_extra_key_none_skips_cooldown() -> None:
    """Test that returning None from the extra key skips the cooldown check."""
    cog = _Cog()
    ctx = _ctx(1)

    async def run() -> object:
        for _ in range(3):
            await cog.pair(ctx)
        return cast("object", await ctx.bot.botkit_cache.get("pair:user:1", namespace="cooldown"))

    assert asyncio.run(run()) is None
    assert cog.calls == 3

# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

from collections.abc import Callable, Sequence
from functools import partial
from typing import Literal, Protocol, overload

from discord.ext import commands

from src import custom
from src.database.models import Guild, User


async def _preload_user(ctx: custom.Context, prefetch_related: Sequence[str]) -> Literal[True]:
    """Preload the user object into the context object.

    Args:
    ----
        ctx: The context object to preload the user object into.
        prefetch_related: List of related fields to prefetch.

    Returns:
    -------
        bool: (True) always.

    """
    if isinstance(ctx, custom.ExtContext):
        ctx.user_obj = (
            await User.get_or_none(id=ctx.author.id).prefetch_related(*prefetch_related) if ctx.author else None
        )
    else:
        ctx.user_obj = await User.get_or_none(id=ctx.user.id).prefetch_related(*prefetch_related) if ctx.user else None
    return True


async def _preload_guild(ctx: custom.Context, prefetch_related: Sequence[str]) -> Literal[True]:
    """Preload the guild object into the context object.

    Args:
    ----
        ctx: The context object to preload the guild object into.
        prefetch_related: List of related fields to prefetch.

    Returns:
    -------
        bool: (True) always.

    """
    ctx.guild_obj = await Guild.get_or_none(id=ctx.guild.id).prefetch_related(*prefetch_related) if ctx.guild else None
    return True


async def _preload_or_create_user(ctx: custom.Context, prefetch_related: Sequence[str]) -> Literal[True]:
    """Preload or create the user object into the context object. If the user object does not exist, create it.

    Args:
    ----
        ctx: The context object to preload or create the user object into.
        prefetch_related: List of related fields to prefetch.

    Returns:
    -------
        bool: (True) always.

    """
    user: User | None
    user, _ = await User.get_or_create(id=ctx.author.id) if ctx.author else (None, None)
    if user is not None:
        await user.fetch_related(*prefetch_related)
    ctx.user_obj = user
    return True


async def _preload_or_create_guild(ctx: custom.Context, prefetch_related: Sequence[str]) -> Literal[True]:
    """Preload or create the guild object into the context object. If the guild object does not exist, create it.

    Args:
    ----
        ctx: The context object to preload or create the guild object into.
        prefetch_related: List of related fields to prefetch.

    Returns:
    -------
        bool: (True) always.

    """
    guild: Guild | None
    guild, _ = await Guild.get_or_create(id=ctx.guild.id) if ctx.guild else (None, None)
    if guild is not None:
        await guild.fetch_related(*prefetch_related)
    ctx.guild_obj = guild
    return True


class PreloadFunction(Protocol):
    async def __call__(self, ctx: custom.Context, prefetch_related: Sequence[str]) -> Literal[True]: ...


@overload
def preload_x[T](f: T, *, preloader: PreloadFunction, prefetch_related: Sequence[str] | None = None) -> T: ...


@overload
def preload_x[T](
    f: None = None, *, preloader: PreloadFunction, prefetch_related: Sequence[str] | None = None
) -> Callable[[T], T]: ...


def preload_x[T](
    f: T | None = None, *, preloader: PreloadFunction, prefetch_related: Sequence[str] | None = None
) -> T | Callable[[T], T]:
    if prefetch_related is None:
        prefetch_related = []

    func = partial(preloader, prefetch_related=prefetch_related)

    check_decorator = commands.check(func)

    return check_decorator(f) if f is not None else check_decorator


preload_guild = partial(preload_x, preloader=_preload_guild)
preload_user = partial(preload_x, preloader=_preload_user)
preload_or_create_guild = partial(preload_x, preloader=_preload_or_create_guild)
preload_or_create_user = partial(preload_x, preloader=_preload_or_create_user)

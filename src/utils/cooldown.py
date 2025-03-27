# Copyright (c) NiceBots
# SPDX-License-Identifier: MIT

import time
from collections.abc import Awaitable, Callable, Coroutine
from enum import Enum
from functools import wraps
from inspect import isawaitable
from typing import Any, Concatenate, cast

import discord
from discord.ext import commands

from src import custom

type ReactiveCooldownSetting[T: Any] = T | Callable[[custom.Bot, custom.Context], T | Coroutine[Any, Any, T]]
type CogCommandFunction[T: commands.Cog, **P] = Callable[Concatenate[T, P], Awaitable[None]]


class BucketType(Enum):
    DEFAULT = "default"  # Uses provided key as is
    USER = "user"  # Per-user cooldown
    MEMBER = "member"  # Per-member (user+guild) cooldown
    GUILD = "guild"  # Per-guild cooldown
    CHANNEL = "channel"  # Per-channel cooldown
    CATEGORY = "category"  # Per-category cooldown
    ROLE = "role"  # Per-role cooldown (uses highest role)


async def parse_reactive_setting[T](value: ReactiveCooldownSetting[T], bot: custom.Bot, ctx: custom.Context) -> T:
    if isinstance(value, type):
        return value  # pyright: ignore [reportReturnType]
    if callable(value):
        value = value(bot, ctx)  # pyright: ignore [reportAssignmentType]
        if isawaitable(value):
            value = await value
    return value  # pyright: ignore [reportReturnType]


class CooldownExceeded(commands.CheckFailure):
    def __init__(self, retry_after: float, bucket_type: BucketType) -> None:
        self.retry_after: float = retry_after
        self.bucket_type: BucketType = bucket_type
        super().__init__(f"You are on {bucket_type.value} cooldown")


def get_bucket_key(ctx: custom.Context, base_key: str, bucket_type: BucketType) -> str:  # noqa: PLR0911
    """Generate a cooldown key based on the bucket type."""
    match bucket_type:
        case BucketType.USER:
            return f"{base_key}:user:{ctx.author.id}"
        case BucketType.MEMBER:
            return f"{base_key}:member:{ctx.guild}:{ctx.author.id}" if ctx.guild else f"{base_key}:user:{ctx.author.id}"
        case BucketType.GUILD:
            return f"{base_key}:guild:{ctx.guild.id}" if ctx.guild else base_key
        case BucketType.CHANNEL:
            return f"{base_key}:channel:{ctx.channel.id}"
        case BucketType.CATEGORY:
            category_id = ctx.channel.category_id if hasattr(ctx.channel, "category_id") else None
            return f"{base_key}:category:{category_id}" if category_id else f"{base_key}:channel:{ctx.channel.id}"
        case BucketType.ROLE:
            if ctx.guild and hasattr(ctx.author, "roles") and isinstance(ctx.author, discord.Member):
                top_role_id = max((role.id for role in ctx.author.roles), default=0)
                return f"{base_key}:role:{top_role_id}"
            return f"{base_key}:user:{ctx.author.id}"
        case _:  # BucketType.DEFAULT
            return base_key


def cooldown[C: commands.Cog, **P](
    key: ReactiveCooldownSetting[str],
    *,
    limit: ReactiveCooldownSetting[int],
    per: ReactiveCooldownSetting[int],
    bucket_type: ReactiveCooldownSetting[BucketType] = BucketType.DEFAULT,
    strong: ReactiveCooldownSetting[bool] = False,
    cls: ReactiveCooldownSetting[type[CooldownExceeded]] = CooldownExceeded,
) -> Callable[[CogCommandFunction[C, P]], CogCommandFunction[C, P]]:
    """Enhanced cooldown decorator that supports different bucket types.

    Args:
        key: Base key for the cooldown
        limit: Number of uses allowed
        per: Time period in seconds
        bucket_type: Type of bucket to use for the cooldown
        strong: If True, adds current timestamp even if limit is reached
        cls: Custom exception class to raise

    """

    def inner(func: CogCommandFunction[C, P]) -> CogCommandFunction[C, P]:
        @wraps(func)
        async def wrapper(self: C, *args: P.args, **kwargs: P.kwargs) -> None:
            ctx: custom.Context = args[0]  # pyright: ignore [reportAssignmentType]
            cache = ctx.bot.botkit_cache
            key_value: str = await parse_reactive_setting(key, ctx.bot, ctx)
            limit_value: int = await parse_reactive_setting(limit, ctx.bot, ctx)
            per_value: int = await parse_reactive_setting(per, ctx.bot, ctx)
            strong_value: bool = await parse_reactive_setting(strong, ctx.bot, ctx)
            cls_value: type[CooldownExceeded] = await parse_reactive_setting(cls, ctx.bot, ctx)
            bucket_type_value: BucketType = await parse_reactive_setting(bucket_type, ctx.bot, ctx)

            # Generate the full cooldown key based on bucket type
            full_key = get_bucket_key(ctx, key_value, bucket_type_value)

            now = time.time()
            time_stamps = cast("tuple[float, ...]", await cache.get(full_key, default=(), namespace="cooldown"))
            time_stamps = tuple(filter(lambda x: x > now - per_value, time_stamps))
            time_stamps = time_stamps[-limit_value:]

            if len(time_stamps) < limit_value or strong_value:
                time_stamps = (*time_stamps, now)
                await cache.set(full_key, time_stamps, namespace="cooldown", ttl=per_value)
                limit_value += 1  # to account for the current command

            if len(time_stamps) >= limit_value:
                raise cls_value(min(time_stamps) - now + per_value, bucket_type_value)

            await func(self, *args, **kwargs)

        return wrapper

    return inner

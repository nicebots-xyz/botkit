# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz


from collections.abc import Callable
from typing import Any

from tortoise.backends.base.client import TransactionContext
from tortoise.transactions import atomic as t_atomic
from tortoise.transactions import in_transaction as t_in_transaction

from src.database.config import APP_CONNECTION_MAPPING


def atomic[F: Callable[..., Any]](connection_name: str | None = None) -> Callable[[F], F]:
    return t_atomic(APP_CONNECTION_MAPPING[connection_name or "models"])


def in_transaction(app_name: str | None = None) -> TransactionContext:  # pyright: ignore[reportMissingTypeArgument, reportUnknownParameterType]
    return t_in_transaction(APP_CONNECTION_MAPPING[app_name or "models"])  # pyright: ignore[reportUnknownVariableType]


__all__ = ("atomic", "in_transaction")

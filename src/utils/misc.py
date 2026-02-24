# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz
from collections.abc import Callable


class LazyProxy[T]:
    def __init__(self, func: Callable[..., T]) -> None:
        self._func: Callable[..., T] = func
        self._value: T | None = None

    def __getattr__(self, name: str) -> T:
        if self._value is None:
            self._value = self._func()
        return getattr(self._value, name)

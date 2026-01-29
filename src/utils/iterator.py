# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

from collections.abc import Iterator


def next_default[T, V](iterator: Iterator[T], default: V = None) -> T | V:
    try:
        return next(iterator)
    except StopIteration:
        return default

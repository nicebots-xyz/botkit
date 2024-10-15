from typing import TypeVar
from collections.abc import Iterator

T = TypeVar("T")
V = TypeVar("V")


def next_default(iterator: Iterator[T], default: V = None) -> T | V:
    try:
        return next(iterator)
    except StopIteration:
        return default

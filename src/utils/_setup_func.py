# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

from collections.abc import Awaitable, Callable
from inspect import signature
from typing import overload


@overload
def setup_func[**P, T](func: Callable[P, Awaitable[T]], *args: P.args, **kwargs: P.kwargs) -> Awaitable[T]: ...


@overload
def setup_func[**P, T](func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T: ...


def setup_func[**P, T](
    func: Callable[P, T] | Callable[P, Awaitable[T]], *args: P.args, **kwargs: P.kwargs
) -> T | Awaitable[T]:
    """Set up a function with the required arguments from the kwargs.

    This function inspects the target function's signature and calls it with
    only the arguments it accepts from the provided kwargs. Arguments with
    default values are optional.

    Args:
        func: The function to call (can be sync or async)
        *args: Positional arguments to pass to the function
        **kwargs: The arguments that may be passed to the function if it requires them

    Returns:
        The result of the function call (can be a coroutine if func is async)

    Raises:
        TypeError: If a required argument is missing from kwargs

    Examples:
        >>> def greet(name: str, greeting: str = "Hello") -> str:
        ...     return f"{greeting}, {name}!"
        >>> setup_func(greet, name="World", greeting="Hi", extra="ignored")
        'Hi, World!'

        >>> async def async_greet(name: str) -> str:
        ...     return f"Hello, {name}!"
        >>> await setup_func(async_greet, name="World")
        'Hello, World!'

    """
    parameters = signature(func).parameters
    if len(args) > 0:
        raise TypeError(f"Too many positional arguments for function '{func.__name__}'")

    for name, parameter in parameters.items():
        if name in kwargs or parameter.default != parameter.empty:
            continue
        raise TypeError(f"Missing required argument '{name}' for function '{func.__name__}'")

    filtered_kwargs = {name: kwargs[name] for name in parameters if name in kwargs}
    return func(*args, **filtered_kwargs)  # pyright: ignore[reportCallIssue]

# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT
# ruff: noqa: S101
import inspect
import os
import warnings
import zipfile
from collections.abc import Callable
from glob import iglob
from types import ModuleType
from typing import Any

import discord
from quart import Quart

from src.log import logger


def check_typing(module: ModuleType, func: Callable, types: dict[str, Any]) -> None:
    signature = inspect.signature(func)
    for name, parameter in signature.parameters.items():
        if name in types and parameter.annotation != types[name]:
            warnings.warn(
                f"Parameter {name} of function {func.__name__} of module {module.__name__} does not have the correct type annotation (is {parameter.annotation} should be {types[name]})",  # noqa: E501
                stacklevel=1,
            )


def check_func(module: ModuleType, func: Callable, max_args: int, types: dict[str, Any]) -> None:
    assert callable(func), f"Function {func.__name__} of module {module.__name__} is not callable"
    signature = inspect.signature(func)
    assert len(signature.parameters) <= max_args, (
        f"Function {func.__name__} of module {module.__name__} has too many arguments"
    )
    assert all(param in types for param in signature.parameters), (
        f"Function {func.__name__} of module {module.__name__} does not accept the correct arguments"
        "({', '.join(types.keys())})"
    )
    # check_typing(module, func, types) # temporarily disabled due to unwanted behavior  # noqa: ERA001


def validate_module(module: ModuleType, config: dict[str, Any] | None = None) -> None:  # pyright: ignore [reportUnusedParameter] # noqa: ARG001
    """Validate the module to ensure it has the required functions and attributes to be loaded as an extension.

    :param module: The module to validate
    :param config: The configuration to validate against.
    """
    if hasattr(module, "setup"):
        check_func(module, module.setup, 2, {"bot": discord.Bot, "config": dict})

    if hasattr(module, "setup_webserver"):
        check_func(
            module,
            module.setup_webserver,
            3,
            {"app": Quart, "bot": discord.Bot, "config": dict},
        )
    assert hasattr(module, "setup_webserver") or hasattr(
        module,
        "setup",
    ), f"Extension {module.__name__} does not have a setup or setup_webserver function"
    if hasattr(module, "on_startup"):
        check_func(
            module,
            module.on_startup,
            3,
            {"app": Quart, "bot": discord.Bot, "config": dict},
        )

    assert hasattr(module, "default"), f"Extension {module.__name__} does not have a default configuration"
    assert isinstance(
        module.default,
        dict,
    ), f"Extension {module.__name__} has a default configuration of type {type(module.default)} instead of dict"
    assert "enabled" in module.default, (
        f"Extension {module.__name__} does not have an enabled key in its default configuration"
    )


def unzip_extensions() -> None:
    for file in iglob("src/extensions/*.zip"):
        with zipfile.ZipFile(file, "r") as zip_ref:
            zip_ref.extractall("src/extensions")
            os.remove(file)
            logger.info(f"Extracted {file}")

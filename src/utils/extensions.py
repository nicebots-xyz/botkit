# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import inspect
import os
import zipfile
import discord
import warnings

from types import ModuleType
from typing import Any, Callable
from glob import iglob
from schema import Schema
from quart import Quart

from src.log import logger


def check_typing(module: ModuleType, func: Callable, types: dict[str, Any]):
    signature = inspect.signature(func)
    for name, parameter in signature.parameters.items():
        if name in types and not parameter.annotation == types[name]:
            warnings.warn(
                f"Parameter {name} of function {func.__name__} of module {module.__name__} does not have the correct type annotation (is {parameter.annotation} should be {types[name]})"
            )


def check_func(
    module: ModuleType, func: Callable, max_args: int, types: dict[str, Any]
):
    assert callable(
        func
    ), f"Function {func.__name__} of module {module.__name__} is not callable"
    signature = inspect.signature(func)
    assert (
        len(signature.parameters) <= max_args
    ), f"Function {func.__name__} of module {module.__name__} has too many arguments"
    assert all(
        param in types for param in signature.parameters.keys()
    ), f"Function {func.__name__} of module {module.__name__} does not accept the correct arguments ({', '.join(types.keys())})"
    check_typing(module, func, types)


# noinspection DuplicatedCode
def validate_module(module: ModuleType, config: dict[str, Any] | None = None) -> None:
    """
    Validate the module to ensure it has the required functions and attributes to be loaded as an extension
    :param module: The module to validate
    :param config: The configuration to validate against
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
        module, "setup"
    ), f"Extension {module.__name__} does not have a setup or setup_webserver function"
    if hasattr(module, "on_startup"):
        check_func(
            module,
            module.on_startup,
            3,
            {"app": Quart, "bot": discord.Bot, "config": dict},
        )

    assert hasattr(module, "default") and isinstance(
        module.default, dict
    ), f"Extension {module.__name__} does not have a default configuration"
    assert (
        "enabled" in module.default
    ), f"Extension {module.__name__} does not have an enabled key in its default configuration"
    if hasattr(module, "schema"):
        assert (
            isinstance(module.schema, Schema) or isinstance(module.schema, dict)
        ), f"Extension {module.__name__} has a schema of type {type(module.schema)} instead of Schema or dict"

        if isinstance(module.schema, dict):
            module.schema = Schema(module.schema)
        if config:
            module.schema.validate(config)
        else:
            try:
                module.schema.validate(module.default)
            except Exception as e:
                warnings.warn(
                    f"Default configuration for extension {module.__name__} does not match schema: {e}"
                )
    else:
        warnings.warn(f"Extension {module.__name__} does not have a schema")


def unzip_extensions():
    for file in iglob("src/extensions/*.zip"):
        with zipfile.ZipFile(file, "r") as zip_ref:
            zip_ref.extractall("src/extensions")
            os.remove(file)
            logger.info(f"Extracted {file}")

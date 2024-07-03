import inspect
import os
import zipfile
import discord

from types import ModuleType
from glob import iglob
from schema import Schema
from flask import Flask

from src.logging import logger


# noinspection DuplicatedCode
def validate_module(module: ModuleType, config: dict = None):
    if hasattr(module, "setup"):
        assert callable(
            module.setup
        ), f"Extension {module.__name__}.setup is not callable"
        signature = inspect.signature(module.setup)
        assert (
            len(signature.parameters) == 2
        ), f"Extension {module.__name__} setup function does not accept two arguments"
        assert list(signature.parameters.keys()) == [
            "bot",
            "config",
        ], f"Extension {module.__name__} setup function does not accept bot and config as arguments"
        if not signature.parameters["bot"].annotation == discord.Bot:
            logger.warning(
                f"Extension {module.__name__} setup function does not have bot typed as discord.Bot"
            )
            print(signature.parameters["bot"].annotation)
        if not signature.parameters["config"].annotation == dict:
            logger.warning(
                f"Extension {module.__name__} setup function does not have config typed as dict"
            )
    if hasattr(module, "setup_webserver"):
        assert callable(
            module.setup_webserver
        ), f"Extension {module.__name__}.setup_webserver is not callable"
        signature = inspect.signature(module.setup_webserver)
        assert (
            len(signature.parameters) == 3
        ), f"Extension {module.__name__} setup_webserver function does not accept three arguments"
        assert list(signature.parameters.keys()) == [
            "app",
            "bot",
            "config",
        ], f"Extension {module.__name__} setup_webserver function does not accept app, bot and config as arguments"
        if not signature.parameters["app"].annotation == Flask:
            logger.warning(
                f"Extension {module.__name__} setup_webserver function does not have app typed as Flask"
            )
            print(signature.parameters["app"].annotation)
        if not signature.parameters["bot"].annotation == discord.Bot:
            logger.warning(
                f"Extension {module.__name__} setup_webserver function does not have bot typed as discord.Bot"
            )
            print(signature.parameters["bot"].annotation)
        if not signature.parameters["config"].annotation == dict:
            logger.warning(
                f"Extension {module.__name__} setup_webserver function does not have config typed as dict"
            )

    assert hasattr(module, "setup_webserver") or hasattr(
        module, "setup"
    ), f"Extension {module.__name__} does not have a setup or setup_webserver function"
    assert hasattr(
        module, "default"
    ), f"Extension {module.__name__} does not have a default configuration"
    assert (
        "enabled" in module.default
    ), f"Extension {module.__name__} does not have an enabled key in its default configuration"
    assert hasattr(module, "schema") and (
        isinstance(module.schema, Schema) or isinstance(module.schema, dict)
    ), f"Extension {module.__name__} does not have a schema attribute of type Schema or dict"

    if isinstance(module.schema, dict):
        try:
            module.schema = Schema(module.schema)
        except Exception as e:
            raise type(e)(str(e).replace("\n", " ").replace("  ", " "))
    module.schema.validate(config or module.default)


def unzip_extensions():
    for file in iglob("src/extensions/*.zip"):
        with zipfile.ZipFile(file, "r") as zip_ref:
            zip_ref.extractall("src/extensions")
            os.remove(file)
            logger.info(f"Extracted {file}")

import os
import zipfile
import inspect
import discord

from glob import iglob
from types import ModuleType
from schema import Schema
from src.logging import logger


def validate_module(module: ModuleType):
    assert hasattr(module, "setup") and callable(
        module.setup
    ), f"Extension {module.__name__} does not have a setup function"
    assert hasattr(
        module, "default"
    ), f"Extension {module.__name__} does not have a default configuration"
    assert (
        "enabled" in module.default
    ), f"Extension {module.__name__} does not have an enabled key in its default configuration"
    assert hasattr(module, "schema") and (
        isinstance(module.schema, Schema) or isinstance(module.schema, dict)
    ), f"Extension {module.__name__} does not have a schema attribute of type Schema or dict"
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

    if isinstance(module.schema, dict):
        try:
            module.schema = Schema(module.schema)
        except Exception as e:
            raise type(e)(str(e).replace("\n", " ").replace("  ", " "))
    module.schema.validate(module.default)


def unzip_extensions():
    for file in iglob("src/extensions/*.zip"):
        with zipfile.ZipFile(file, "r") as zip_ref:
            zip_ref.extractall("src/extensions")
            os.remove(file)
            logger.info(f"Extracted {file}")

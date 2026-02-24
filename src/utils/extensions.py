# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz
# ruff: noqa: S101
import os
import zipfile
from glob import iglob
from types import ModuleType

from src.log import logger
from src.startup.types import SetupFunction, SetupWebserverFunction, StartupFunction


def validate_module(module: ModuleType, config: dict[str, object] | None = None) -> None:  # noqa: ARG001
    """Validate the module to ensure it has the required functions and attributes to be loaded as an extension.

    Args:
        module: The module to validate
        config: The configuration to validate against (currently unused)

    Raises:
        AssertionError: If the module doesn't meet extension requirements

    """
    if hasattr(module, "setup"):
        assert isinstance(module.setup, SetupFunction), (
            f"Extension {module.__name__} has an invalid setup function signature"
        )

    if hasattr(module, "setup_webserver"):
        assert isinstance(module.setup_webserver, SetupWebserverFunction), (
            f"Extension {module.__name__} has an invalid setup_webserver function signature"
        )

    assert hasattr(module, "setup_webserver") or hasattr(
        module,
        "setup",
    ), f"Extension {module.__name__} does not have a setup or setup_webserver function"

    if hasattr(module, "on_startup"):
        assert isinstance(module.on_startup, StartupFunction), (
            f"Extension {module.__name__} has an invalid on_startup function signature"
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

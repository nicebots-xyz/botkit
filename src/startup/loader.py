# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

"""Extension loading and initialization logic."""

import importlib
from glob import iglob
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from src import i18n
from src.config import config
from src.i18n.classes import ExtensionTranslation
from src.log import logger
from src.startup.types import (
    SetupFunctionList,
    StartupFunctionList,
    WebserverFunctionList,
)

if TYPE_CHECKING:
    from types import ModuleType


def find_translation_file(extension_path: Path, extension_name: str) -> Path | None:
    """Find translation file for an extension using centralized path resolution.

    Searches in the following order:
    1. extension_path/translations.yml
    2. extension_path/translations.yaml
    3. src/translations/{extension_name}.yml
    4. src/translations/{extension_name}.yaml

    Args:
        extension_path: Path to the extension directory
        extension_name: Name of the extension

    Returns:
        Path to the translation file if found, None otherwise

    """
    candidates = [
        extension_path / "translations.yml",
        extension_path / "translations.yaml",
        Path(__file__).parent.parent / "translations" / f"{extension_name}.yml",
        Path(__file__).parent.parent / "translations" / f"{extension_name}.yaml",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def load_extensions() -> tuple[
    SetupFunctionList,
    WebserverFunctionList,
    StartupFunctionList,
    list[ExtensionTranslation],
]:
    """Load extensions from the extensions directory.

    Returns:
        A tuple containing:
        - bot_functions: List of (setup_function, config) tuples for bot setup
        - back_functions: List of (setup_webserver_function, config) tuples for backend setup
        - startup_functions: List of (on_startup_function, config) tuples for startup hooks
        - translations: List of loaded extension translations

    """
    from src.utils import validate_module  # noqa: PLC0415

    bot_functions: SetupFunctionList = []
    back_functions: WebserverFunctionList = []
    startup_functions: StartupFunctionList = []
    translations: list[ExtensionTranslation] = []

    for _extension in iglob("src/extensions/*"):
        extension_path = Path(_extension)
        name = extension_path.name

        # Skip special files
        if name.endswith(("_", "_/", ".py")):
            continue

        # Check if extension is enabled in config
        _, its_config = config.get_extension(name, {})
        if its_config and not its_config.get("enabled"):
            continue

        # Try to import the extension module
        try:
            module: ModuleType = importlib.import_module(f"src.extensions.{name}")
        except ImportError as e:
            logger.error(f"Failed to import extension {name}")
            logger.debug("", exc_info=e)
            continue

        # Get the extension's config (from config file or module's default)
        module_default: dict[str, Any] = getattr(module, "default", {})
        its_config = its_config or module_default
        if not its_config.get("enabled"):
            del module
            continue

        logger.info(f"Loading extension {name}")

        # Load translations if available
        translation_path = find_translation_file(extension_path, name)
        if translation_path is not None:
            try:
                translation = i18n.load_translation(str(translation_path))
                translations.append(translation)

                # Store translation for later use
                if translation.strings:
                    its_config["translations"] = translation.strings
            except yaml.YAMLError as e:
                logger.error(f"Error loading translation {translation_path}: {e}")
        else:
            logger.warning(f"No translation found for extension {name}")

        # Validate the module structure
        validate_module(module, its_config)

        # Register extension functions
        # Type checkers can't infer the exact types from hasattr/callable checks,
        # so we use type: ignore to suppress false positives
        if hasattr(module, "setup") and callable(module.setup):
            bot_functions.append((module.setup, its_config))  # pyright: ignore[reportArgumentType]

        if hasattr(module, "setup_webserver") and callable(module.setup_webserver):
            back_functions.append((module.setup_webserver, its_config))  # pyright: ignore[reportArgumentType]

        if hasattr(module, "on_startup") and callable(module.on_startup):
            startup_functions.append((module.on_startup, its_config))  # pyright: ignore[reportArgumentType]

    return bot_functions, back_functions, startup_functions, translations


__all__ = ["find_translation_file", "load_extensions"]

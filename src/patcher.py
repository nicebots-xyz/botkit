# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

import importlib.util
import inspect
import os
from glob import iglob

from src.config import config
from src.log import logger
from src.utils import setup_func


async def load_and_run_patches() -> None:
    for patch_file in iglob("src/extensions/*/patch.py"):
        extension = os.path.basename(os.path.dirname(patch_file))
        _, its_config = config.get_extension(extension, {})
        if not its_config.get("enabled", False):
            continue
        logger.info(f"Loading patch for extension {extension}")
        spec = importlib.util.spec_from_file_location(f"src.extensions.{extension}.patch", patch_file)
        if not spec or not spec.loader:
            continue
        patch_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(patch_module)
        if hasattr(patch_module, "patch") and callable(patch_module.patch):
            result = setup_func(patch_module.patch, config=its_config)
            if inspect.isawaitable(result):
                await result

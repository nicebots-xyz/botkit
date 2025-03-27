# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# the above line allows us to import from src without any issues whilst using src/__main__.py
import importlib.util
from glob import iglob

from src.config import config
from src.log import logger
from src.utils.setup_func import setup_func


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
            await setup_func(patch_module.patch, config=its_config)

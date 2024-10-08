from src.config import config
import os
import importlib.util
import asyncio
from glob import iglob
from src.logging import logger
from src.utils.setup_func import setup_func
from src.start import main


async def load_and_run_patches():
    for patch_file in iglob("src/extensions/*/patch.py"):
        extension = os.path.basename(os.path.dirname(patch_file))
        if config["extensions"].get(extension, {}).get("enabled", False):
            logger.info(f"Loading patch for extension {extension}")
            spec = importlib.util.spec_from_file_location(
                f"src.extensions.{extension}.patch", patch_file
            )
            if not spec or not spec.loader:
                continue
            patch_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(patch_module)
            if hasattr(patch_module, "patch") and callable(patch_module.patch):
                await setup_func(
                    patch_module.patch, config=config["extensions"][extension]
                )


async def pre_main():
    await load_and_run_patches()
    await main()


if __name__ == "__main__":

    asyncio.run(pre_main())

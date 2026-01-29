# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# the above line allows us to import from src without any issues whilst using src/__main__.py
import asyncio

from src.patcher import load_and_run_patches


async def main() -> None:
    await load_and_run_patches()
    # we import main here to apply patches before importing as many things we can
    # and allow the patches to be applied to later imported modules
    from src.start import start  # noqa: PLC0415

    await start()


if __name__ == "__main__":
    asyncio.run(main())

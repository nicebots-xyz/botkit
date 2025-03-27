# Copyright (c) NiceBots
# SPDX-License-Identifier: MIT

from logging import getLogger

import aerich
from tortoise import Tortoise

from src.config import config

logger = getLogger("bot").getChild("database")

TORTOISE_ORM = {
    "connections": {"default": config.db.url},
    "apps": {
        "models": {
            "models": ["src.database.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}


async def init() -> None:
    command = aerich.Command(
        TORTOISE_ORM,
        app="models",
        location="./src/database/migrations/",
    )
    await command.init()
    migrated = await command.upgrade(run_in_transaction=True)
    logger.success(f"Successfully migrated {migrated} migrations")  # pyright: ignore [reportAttributeAccessIssue]
    await Tortoise.init(config=TORTOISE_ORM)


async def shutdown() -> None:
    await Tortoise.close_connections()


__all__ = ["init", "shutdown"]

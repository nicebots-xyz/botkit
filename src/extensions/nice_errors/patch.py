# Copyright NiceBots - All rights reserved 2026

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any

from src.custom import CustomBot
from src.log import logger as base_logger

logger = base_logger.getChild("nice_errors")


async def _run_event(
    self: CustomBot,
    coro: Callable[..., Coroutine[Any, Any, Any]],
    event_name: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    try:
        await coro(*args, **kwargs)
    except asyncio.CancelledError:
        pass
    except Exception as exc:  # noqa: BLE001
        try:  # noqa: SIM105
            await self.on_error(event_name, *args, **kwargs, exc=exc)
        except asyncio.CancelledError:
            pass


async def patch(config: dict[str, Any]) -> None:
    sentry_sdk = None
    if (sentry_config := config.get("sentry", {})).get("dsn"):
        import sentry_sdk  # noqa: PLC0415
        from sentry_sdk.integrations.asyncio import AsyncioIntegration  # noqa: PLC0415
        from sentry_sdk.integrations.logging import LoggingIntegration  # noqa: PLC0415
        from sentry_sdk.scrubber import (  # noqa: PLC0415
            DEFAULT_DENYLIST,
            DEFAULT_PII_DENYLIST,
            EventScrubber,
        )

        sentry_sdk.init(
            dsn=sentry_config["dsn"],
            environment=sentry_config.get("environment", "production"),
            integrations=[
                AsyncioIntegration(),
                LoggingIntegration(),
            ],
            event_scrubber=EventScrubber(
                denylist=[*DEFAULT_DENYLIST, "headers", "kwargs"],
                pii_denylist=[*DEFAULT_PII_DENYLIST, "headers", "kwargs"],
            ),
        )
        logger.success("Sentry SDK initialized")

    CustomBot._run_event = _run_event  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
    logger.success("Patched CustomBot._run_event")

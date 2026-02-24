# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

from typing import TYPE_CHECKING

from .bot_config import raw_config
from .models import Config

# Lazy load Config object
if TYPE_CHECKING:
    config: Config
else:
    _config_obj: Config | None = None

    def __getattr__(name: str) -> Config:
        if name == "config":
            global _config_obj  # noqa: PLW0603
            if _config_obj is None:
                _config_obj = Config(**raw_config) if raw_config else Config()
            return _config_obj
        raise AttributeError(name)


__all__ = ["config"]

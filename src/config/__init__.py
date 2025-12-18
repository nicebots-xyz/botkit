# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

from typing import TYPE_CHECKING, Any

from .bot_config import _config
from .models import Config

# Lazy load Config object
if TYPE_CHECKING:
    config: Config
else:
    _config_obj: Config | None = None

    def __getattr__(name: str) -> Any:
        if name == "config":
            global _config_obj  # noqa: PLW0603
            if _config_obj is None:
                _config_obj = Config(**_config) if _config else Config()
            return _config_obj
        raise AttributeError(name)


__all__ = ["config"]

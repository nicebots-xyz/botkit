# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

import os

# Importing anything from inside an extension package (e.g. `src.extensions.<ext>.logic`) runs
# that package's `__init__.py`, which pulls in `src.custom` -> `src.config`, whose lazily-built
# `Config` singleton requires `bot.token`. CI has no `.env`, so without this the first test module
# that imports an extension submodule fails collection entirely. Set a harmless default before any
# test module is imported; `setdefault` keeps a real token if one is already set in the environment.
os.environ.setdefault("BOTKIT__BOT__TOKEN", "test-token-for-pytest")

<!--
SPDX-License-Identifier: MIT
Copyright: 2024-2026 NiceBots.xyz
-->
# API reference

Reference for extension loading and startup entry points.

## Extension loader

::: src.startup.loader
    options:
      members:
        - load_extensions
        - find_translation_file
      show_submodules: false

## Extension utilities

::: src.utils.extensions
    options:
      members:
        - validate_module
        - unzip_extensions
      show_submodules: false

## Startup orchestration

::: src.start
    options:
      members:
        - start
      show_submodules: false

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
      show_submodules: false

## Translations

::: src.i18n.utils
    options:
      members:
        - find_translation_file
        - load_translation
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

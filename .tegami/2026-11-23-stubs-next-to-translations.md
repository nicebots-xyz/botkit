---
packages:
  botkit: minor
---

## Translation stubs sit next to their translations

`pdm run i18n-stubs` writes each translation file's stub as the Python module at the same path, so `my_ext/translations.yml` is typed by `my_ext/translations.py`. In a `translations/` folder, every file gets its own module, such as `translations/commands/ping.py` for `translations/commands/ping.yml`, and the folders leading to them become packages. An extension without translations of its own gets its stubs next to the centralized file, as `src/translations/my_ext.py`. Stubs left without translations are removed, and `--check` reports them.

Breaking changes:

- `translation_types.py` is now `translations.py`, so `from .translation_types import PingCommandStrings` becomes `from .translations import PingCommandStrings`.
- A translations folder no longer turns its subfolders without any YAML file into keys, so the `__pycache__` of its stubs is ignored.

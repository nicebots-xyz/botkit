---
packages:
  botkit: minor
---

## Bots can override the translations of an extension

An extension's own `translations.yml` now defines its strings and its stubs, and a bot adapts them for itself in `src/translations/<extension>.yml`. Both are merged, so an override only needs the strings and locales it changes, and shared extensions keep the same stubs in every bot. Overrides may not use format arguments that the extension's `en-US` text does not, so that its typed `format` stays correct.

Breaking changes:

- `src/translations/<extension>.yml` is merged over the extension's own translations, where it used to be ignored when both existed.
- `i18n.find_translation_file` is replaced by `i18n.find_translation_files`, which returns every layer, and `i18n.load_translation` accepts several paths.

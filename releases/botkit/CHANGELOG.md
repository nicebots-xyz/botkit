## botkit@0.5.0

### Remove prefix and bridge commands

Botkit now runs on a plain `discord.Bot` and only supports application commands. The `bot.prefix` setting is gone and is ignored if still present, and the bot never requests the `message_content` intent.

Breaking changes for extensions:

- `custom.ExtContext` and the `custom.Context` alias are removed, use `custom.ApplicationContext`.
- `custom.ApplicationContext` extends `discord.ApplicationContext` instead of `bridge.BridgeApplicationContext`.
- `CooldownExceeded` extends `discord.CheckFailure` instead of `commands.CheckFailure`.
- `nice_errors` no longer listens to `on_command_error`.
- Cogs should extend `discord.Cog` instead of `commands.Cog`.

### Translation stubs sit next to their translations

`pdm run i18n-stubs` writes each translation file's stub as the Python module at the same path, so `my_ext/translations.yml` is typed by `my_ext/translations.py`. In a `translations/` folder, every file gets its own module, such as `translations/commands/ping.py` for `translations/commands/ping.yml`, and the folders leading to them become packages. An extension without translations of its own gets its stubs next to the centralized file, as `src/translations/my_ext.py`. Stubs left without translations are removed, and `--check` reports them.

Breaking changes:

- `translation_types.py` is now `translations.py`, so `from .translation_types import PingCommandStrings` becomes `from .translations import PingCommandStrings`.
- A translations folder no longer turns its subfolders without any YAML file into keys, so the `__pycache__` of its stubs is ignored.

### Bots can override the translations of an extension

An extension's own `translations.yml` now defines its strings and its stubs, and a bot adapts them for itself in `src/translations/<extension>.yml`. Both are merged, so an override only needs the strings and locales it changes, and shared extensions keep the same stubs in every bot. Overrides may not use format arguments that the extension's `en-US` text does not, so that its typed `format` stays correct.

Breaking changes:

- `src/translations/<extension>.yml` is merged over the extension's own translations, where it used to be ignored when both existed.
- `i18n.find_translation_file` is replaced by `i18n.find_translation_files`, which returns every layer, and `i18n.load_translation` accepts several paths.

## botkit@0.4.0

### Spend fewer CI minutes on pull requests



### Tests run without a database

Tests turn the database off, and a disabled database no longer loads an SSL certificate.

### Faster, validated and typed translations

Translations are localized once per locale and cached, with `{commands.x}` and `{emojis.x}` filled in at that point instead of on every access. The bot refuses to start when one of these placeholders references a command or app emoji that does not exist.

`pdm run i18n-stubs` generates a `translation_types.py` protocol module per extension, and CI checks that it is up to date. Annotating a slash command with `custom.ApplicationContext[PingCommandStrings]` types `ctx.translations`, and `i18n.typed` types other localized views. Strings with format fields are typed with a `format` method that only accepts those fields, and a locale using a field its `en-US` text lacks fails to load.

A translation can be a `translations/` folder whose files and subfolders become nested keys.

Every string must now include `en-US`, and locales Discord does not support fail to load. `TranslationWrapper` is replaced by `Strings`, and `/ping` in the example "ping" extension is now exclusive a slash command.

### Translation stubs for context menu commands

`pdm run i18n-stubs` no longer fails on commands whose names contain spaces or punctuation, such as the context menu command `Extract text (OCR)`, whose strings are typed by `ExtractTextOCRCommandStrings`.

### Remove the command not found handler

The `nice_errors` extension no longer handles `CommandNotFound` for prefix commands. The closest command suggestion and its "Run x instead" button are removed, along with the `error_command_not_found` and `run_x_instead` translations.

### Separate Renovate pull requests per ecosystem

Non-major updates are grouped per ecosystem, with Python and JavaScript dependencies in separate weekly pull requests, and Python interpreter upgrades leave the group, so a failing interpreter bump no longer blocks every other update. Changelog entries of dependency updates list every package with both versions. Cooldowns, titles and lock file maintenance now come from the shared Renovate preset, and the quality checks install the licensor release of the pinned setup-licensor action.

### Upgrade pnpm to v12.20.0

## botkit@0.3.0

### Per connection database SSL

Each `db.extra_apps` entry can set `params.ssl` to enable or disable verified TLS for its own connection. Entries without it keep following the top-level `db.params.ssl`.

### Replace autofix.ci with NiceBots Autofixer



### Weekly cleanup of old container images



### Remove certifi cooldown bypass



### S3 storages for database models

`db.s3` and `db.extra_apps.<app>.s3` configure S3-compatible storages for `S3Field` columns from `tortoise-extensions`, with SSL toggled per storage. Setting `type: memory` or `type: local` swaps a storage for an in-memory or on-disk one for tests and local development. Extra apps without `s3` follow the top-level `db.s3`.

### Upgrade amannn/action-semantic-pull-request action to v6.1.2



### Upgrade docker/login-action action to v4.8.0



### Upgrade nicebots-xyz/licensor action to v0.1.2



### Upgrade pnpm to v12.18.0



### Upgrade pnpm/action-setup action to v6.1.1

## botkit@0.2.0

### Bots built on Botkit need no configuration

Botkit's release line becomes read only as soon as a repository adds a release line of its own, so the optional `scripts/tegami.local.mts` file is gone. Merging Botkit into a bot no longer conflicts on release configuration.

### Changelog entries for every Renovate dependency update

Renovate dependency update pull requests now get a `patch` changelog entry whatever they update, including dev tooling, GitHub Actions and Docker. Only lock file maintenance is skipped.

### Changelog entries for Renovate dependency updates

Renovate pull requests that update a runtime dependency (`fix(deps): ...`) now get a `patch` changelog entry automatically, committed by the fixer GitHub App. Dev tooling, GitHub Actions and lock file maintenance are skipped.

Setup is described in the "Dependency updates" section of the releases documentation: install the fixer GitHub App on the repository and add a `fixer` environment with `FIXER_APP_CLIENT_ID` and `FIXER_APP_PRIVATE_KEY`.

### No release preview comment on bot pull requests

Pull requests opened by bots, such as Renovate and the Version Packages pull request, no longer get the Tegami preview comment.

### Version Packages pull request passes the repository checks

The pull request is titled `chore(release): version packages` to satisfy the semantic title check, and the generated `releases/*/CHANGELOG.md` files are exempt from the license header check.

### Upgrade docker/login-action action to v4.7.0



### Upgrade pnpm to v12



### Upgrade pnpm/action-setup digest to ea17c68

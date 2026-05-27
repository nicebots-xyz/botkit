<!--
SPDX-License-Identifier: MIT
Copyright: 2024-2026 NiceBots.xyz
-->
# Botkit

Botkit is a **Python 3.12** application template and runtime for Discord bots built on **[py-cord](https://github.com/Pycord-Development/pycord)** (bridge-style bot with optional prefix commands). It wires together:

- **Extensions** under `src/extensions/` — each folder is a feature module discovered at startup.
- **YAML + environment configuration** merged at load time (`BOTKIT__` prefix for env vars).
- An optional **FastAPI** backend (Uvicorn) that can share a process with the bot.
- **Internationalization** helpers and translation YAML per extension.
- Optional **Tortoise ORM** + Aerich migrations when `db` is enabled.

It is a **framework and project layout**, not a single-purpose bot product. You implement behavior in extensions and ship your own `config.yml` / secrets.

## Documentation map

| Page | What you will learn |
|------|---------------------|
| [Getting started](getting-started.md) | Clone, install with PDM, minimal config, first extension, run the bot |
| [Configuration](configuration.md) | Full reference: YAML sections, env vars, process layout, cache |
| [Extensions](extensions.md) | Required exports, examples, patches, translations, logging |
| [Runtime](runtime.md) | What starts when you run the bot, hook order, REST vs backend |
| [Internationalization](i18n.md) | `translations.yml`, slash command locales, `ctx.translations` |
| [Database](database.md) | Enabling Tortoise, URLs, SSL, migrations |
| [Scripts](scripts.md) | `convert-config`, `check-listings` |
| [Deployment](deployment.md) | Docker image, env-first deploys, health checks |
| [Development](development.md) | Working on *your* bot with the template tooling |
| [Contributing](contributing.md) | Pull requests to the Botkit repo, docs build, commit conventions |
| [API reference](api.md) | Extension loader and startup APIs |

## Quick links

- Repository: [github.com/nicebots-xyz/botkit](https://github.com/nicebots-xyz/botkit)
- Example config: `config.example.yaml` in the repo root
- Bundled extensions under `src/extensions/` may include a small `readme.md` each — this site covers **Botkit mechanics**, not every bundled feature's options.

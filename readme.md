<!--
SPDX-License-Identifier: MIT
Copyright: 2024-2026 NiceBots.xyz
-->

# Botkit

Botkit is a **Python 3.12** layout and runtime for **Discord** bots using **[py-cord](https://github.com/Pycord-Development/pycord)** (bridge bot, optional prefix commands), optional **FastAPI** + Uvicorn, YAML configuration with **`BOTKIT__`** environment overrides, per-extension **i18n**, optional **Tortoise ORM**, and a first-party **extension** model under `src/extensions/`.

It is a **framework and template**, not a single finished bot product.

## Documentation

**[docs.nicebots.xyz/botkit](https://docs.nicebots.xyz/botkit/)**

## Quick start

```bash
pdm install
cp config.example.yaml config.yaml   # or config.yml
# edit config.yaml — set bot.token, use.bot / use.backend, extensions
pdm run start
```

See [Getting started](https://docs.nicebots.xyz/botkit/getting-started/) for your first extension.

## Requirements

- [PDM](https://pdm-project.org/latest/)
- Python **3.12**
- A Discord bot token from the [Developer Portal](https://discord.com/developers/applications)

## Repository layout (high level)

| Path | Role |
|------|------|
| `src/extensions/` | One package per feature; discovered automatically |
| `src/start.py` | Async orchestration: DB, unzip, load extensions, bot and/or backend |
| `src/config/` | YAML + env merge → Pydantic `Config` |
| `src/custom/` | `CustomBot`, application contexts, shared cache |
| `docs/` | Published documentation sources |

Bundled extensions under `src/extensions/` may include their own short `readme.md` files for feature-specific options.

## Scripts

- `pdm run start` — run the bot / backend entrypoint (`python src`)
- `pdm run convert-config` — convert between `config.yml` and `BOTKIT__` env files
- `pdm run check-listings` — optional dev tool for bot listing pages (see docs)

## Contributing to Botkit

Pull requests to this repository: [Contributing](https://docs.nicebots.xyz/botkit/contributing/).

## Support

- [Issues](https://github.com/nicebots-xyz/botkit/issues)
- [Discord](https://paill.at/OjTuQ)

## License

[MIT](LICENSE).

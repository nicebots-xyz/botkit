<!--
SPDX-License-Identifier: MIT
Copyright: 2024-2026 NiceBots.xyz
-->
# Runtime

## Starting the bot

```bash
pdm run start
```

Equivalent to **`python src`**. Botkit will:

1. Apply your **logging** settings
2. Run **`patch.py`** for enabled extensions (if any)
3. Connect to the database (if **`db.enabled`**)
4. Load enabled **extensions**
5. Start Discord and/or the HTTP backend according to **`use`**

Startup stops immediately if **`bot.token`** is missing.

---

## What `use.bot` and `use.backend` do

| Setting | You get |
|---------|---------|
| **`use.bot: true`** | Extensions' **`setup()`** runs; bot connects to Discord (gateway or REST mode) |
| **`use.backend: true`** | Extensions' **`setup_webserver()`** runs; FastAPI serves on **`backend.host`** / **`backend.port`** |
| Both **`true`** | One process, one bot instance, Discord + your HTTP routes together |
| Both **`false`** | Nothing to run — startup exits |

**Backend-only** (`use.bot: false`, `use.backend: true`): the bot logs in so your routes can read **`bot.user`**, but the gateway consumer does not run unless your code starts it.

---

## REST mode vs FastAPI backend

Two different HTTP setups — **do not enable both in one process**:

| Mode | Config | Purpose |
|------|--------|---------|
| **REST bot** | `bot.rest.enabled: true` | py-cord interactions server (needs **`pycord-rest`**, **`bot.public_key`**) |
| **Botkit backend** | `use.backend: true` | Your FastAPI routes from extensions |

If both are on, Botkit exits with an error. Use one mode or separate deployments.

---

## Application commands

Botkit runs a plain py-cord **`discord.Bot`**: slash, user and message commands only, without prefix commands or the **`message_content`** intent.

| Config | Effect |
|--------|--------|
| **`bot.slash.enabled: true`** | Application commands are registered |
| **`bot.slash.enabled: false`** | Application commands cleared at startup |

---

## Extension hooks (order)

For a typical **`use.bot: true`** start:

1. Enabled extensions imported
2. **`setup(bot, config)`** called for each
3. Command translations applied from **`translations.yml`**
4. **`on_startup`** hooks awaited (bot may not be online yet — avoid sending messages here)
5. Bot connects to Discord
6. **`{commands.x}`** and **`{emojis.x}`** placeholders work in translations ([Internationalization](i18n.md))

For **`use.backend: true`**, **`setup_webserver(app, bot, config)`** runs before the HTTP server listens.

---

## Shared cache in combined mode

With **`use.bot`** and **`use.backend`** both true, one bot object and one in-memory cache are shared. For multiple replicas, set **`bot.cache.type: redis`** ([Configuration](configuration.md)).

---

## Zip extensions

Any **`src/extensions/*.zip`** is extracted at startup before extensions load. The archive is deleted after extraction.

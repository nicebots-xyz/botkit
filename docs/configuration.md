<!--
SPDX-License-Identifier: MIT
Copyright: 2024-2026 NiceBots.xyz
-->
# Configuration

Botkit reads a YAML config file from the project root and merges **environment variables** on top. Env values override YAML for the same setting.

## Config file

| File | Used when |
|------|-----------|
| `config.yaml` | Present (preferred) |
| `config.yml` | `config.yaml` is missing |

Copy **`config.example.yaml`** as a starting point. Config files are gitignored — do not commit tokens.

You can run with **env vars only** (no file), but you must still set **`bot.token`**.

## Precedence

1. Values from **`config.yaml`** / **`config.yml`**
2. Overridden by **`BOTKIT__…`** or **`BOTKIT_FILE__…`** environment variables (and `.env` if present)

Nested settings merge: env can change one key without replacing an entire section.

---

## Environment variables

Prefix every key with **`BOTKIT__`**. Nested paths use **`__`** (lowercase):

| YAML | Environment variable |
|------|----------------------|
| `bot.token` | `BOTKIT__bot__token` |
| `use.backend` | `BOTKIT__use__backend` |
| `extensions.ping.enabled` | `BOTKIT__extensions__ping__enabled` |

Boolean env values: `true` / `false`. Lists and objects: use JSON in the value:

```env
BOTKIT__extensions__branding__status__playing=["with stuff","with things"]
```

Convert YAML ↔ env with **`pdm run convert-config`** ([Scripts](scripts.md)).

### File-backed values

Use **`BOTKIT_FILE__`** instead of **`BOTKIT__`** to set a value from a file. The environment variable contains the file path, and the file contents become the configuration value. Nested paths use the same **`__`** separator:

```env
BOTKIT_FILE__bot__token=/run/secrets/discord_token
BOTKIT_FILE__bot__cache__redis__password=/run/secrets/redis_password
```

This is useful with container secret mounts. Leading and trailing whitespace, including the terminal newline commonly added when creating a secret file, is removed. File-backed values are then parsed like direct environment values, so values such as `true` and JSON retain their normal types.

---

## `use` — what starts

```yaml
use:
  bot: true      # Discord client
  backend: false # HTTP API (FastAPI)
```

| Key | Default | Effect |
|-----|---------|--------|
| `bot` | `true` | Run Discord extensions (`setup`) and connect to Discord |
| `backend` | `false` | Run HTTP extensions (`setup_webserver`) on Uvicorn |

| `use.bot` | `use.backend` | Typical use |
|-----------|---------------|-------------|
| `true` | `false` | Discord-only bot |
| `false` | `true` | HTTP API with bot login, no gateway in this process |
| `true` | `true` | Bot + your routes in one process |

!!! warning "REST mode vs backend"
    **`bot.rest.enabled: true`** and **`use.backend: true`** cannot be used together in one process. Choose one or run separate processes.

### Process layout

Common combinations of **`use`**, **`bot.cache`**, and **`bot.rest`**:

| Layout | Config | Notes |
|--------|--------|-------|
| Discord bot only | `use.bot: true`, `use.backend: false` | Default setup |
| Bot + HTTP API | `use.bot: true`, `use.backend: true` | One process; in-memory cache is fine |
| HTTP API only | `use.bot: false`, `use.backend: true` | Bot logs in for routes; no gateway in this process |
| Multiple replicas | `bot.cache.type: redis` | Required when more than one process needs shared cache |
| REST interactions | `bot.rest.enabled: true` | Do **not** set `use.backend: true` in the same process |

---

## `bot` — Discord client

```yaml
bot:
  token: "…"
  public_key: null
  slash:
    enabled: true
  prefix:
    prefix: "!"
    enabled: false
  cache:
    type: memory
    redis:
      host: localhost
      port: 6379
      db: 0
      password: null
      ssl: false
  rest:
    enabled: false
    health: false
    host: "0.0.0.0"
    port: 6000
  cache_app_emojis: true
```

### `bot.token`

Required. From the [Discord Developer Portal](https://discord.com/developers/applications).

### `bot.slash`

| Key | Default | Effect |
|-----|---------|--------|
| `enabled` | `false` | Set `true` to register slash commands |

Match **`config.example.yaml`** unless you intentionally want prefix-only commands.

### `bot.prefix`

Prefix / bridge commands. Shorthand or object:

```yaml
bot:
  prefix: "!"
# or
bot:
  prefix:
    prefix: "!"
    enabled: true
```

Default: prefix **`!`**, **disabled**. When disabled, prefix commands are off and the bot does not request **`message_content`** intent.

### `bot.cache`

Shared cache for extensions (`bot.botkit_cache`).

| `type` | When to use |
|--------|-------------|
| `memory` | Single process (default) |
| `redis` | Multiple containers/replicas |

```yaml
bot:
  cache:
    type: redis
    redis:
      host: localhost
      port: 6379
      db: 0
      ssl: false
```

If you set `type: redis` but omit `redis` settings, Botkit falls back to memory and logs a warning.

### `bot.rest`

Interactions-over-HTTP mode (requires **`pycord-rest`** and **`bot.public_key`**). Not compatible with **`use.backend`** in the same process.

| Key | Default | Role |
|-----|---------|------|
| `enabled` | `false` | REST bot instead of gateway |
| `health` | `false` | Health check endpoint |
| `host` / `port` | `0.0.0.0` / `6000` | Listen address for REST server |

### `bot.cache_app_emojis`

Default **`true`**. Needed for **`{emojis.name}`** placeholders in translations ([Internationalization](i18n.md)).

---

## `backend` — HTTP API

When **`use.backend: true`**:

```yaml
backend:
  host: "0.0.0.0"
  port: 5000
  access_log: true
  server_header: false
```

Extensions add routes in **`setup_webserver(app, bot, config)`**.

---

## `logging`

```yaml
logging:
  level: INFO
  console: true
  file: false
  directory: logs
```

| Level | Typical use |
|-------|-------------|
| `DEBUG` | Verbose troubleshooting |
| `INFO` | Normal operation |
| `WARNING` | Misconfiguration, deprecations |
| `ERROR` / `CRITICAL` | Failures |

Set **`file: true`** to write logs under **`directory`**.

---

## `extensions` — per-feature settings

```yaml
extensions:
  ping:
    enabled: true
  branding:
    enabled: true
    embed:
      color: "#ffffff"
```

Each key matches a folder under **`src/extensions/<name>/`**. **`nice_errors`** and **`nice-errors`** are treated as the same extension.

| Situation | What happens |
|-----------|--------------|
| No YAML entry for an extension | Uses **`default`** from the extension's Python code |
| YAML entry present | Uses YAML values; not merged with `default` key-by-key |
| `enabled: false` | Extension is not loaded |
| `enabled: false` in `default` only | Off unless YAML sets `enabled: true` |

Extension-specific options (tokens, URLs, colors, etc.) are documented in each extension's **`readme.md`**. Translation text comes from **`translations.yml`**, not from config YAML.

If an extension has **`patch.py`**, it runs only when that extension is **enabled** ([Runtime](runtime.md)).

---

## `db` — optional database

Off by default. See [Database](database.md).

```yaml
db:
  enabled: true
  url: "postgres://user:pass@localhost:5432/botkit"
```

When enabled, migrations run automatically before extensions load.

---

## Examples

**Minimal Discord bot:**

```yaml
bot:
  token: "your-token"
  slash:
    enabled: true
use:
  bot: true
  backend: false
extensions:
  ping:
    enabled: true
logging:
  level: INFO
  console: true
```

**Bot + HTTP in one process (Redis cache):**

```yaml
bot:
  token: "your-token"
  slash:
    enabled: true
  cache:
    type: redis
    redis:
      host: redis
      port: 6379
      db: 0
      ssl: false
use:
  bot: true
  backend: true
backend:
  port: 5000
extensions:
  ping:
    enabled: true
```

**Env-only:**

```env
BOTKIT__bot__token=your-token
BOTKIT__bot__slash__enabled=true
BOTKIT__use__bot=true
BOTKIT__extensions__ping__enabled=true
```

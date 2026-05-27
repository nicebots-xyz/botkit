<!--
SPDX-License-Identifier: MIT
Copyright: 2024-2026 NiceBots.xyz
-->
# Extensions

Each feature lives in its own folder under **`src/extensions/<name>/`**. Botkit loads every enabled extension at startup and connects it to Discord and/or your HTTP API.

## Finding and enabling extensions

1. Put code in **`src/extensions/<name>/`** (one folder per feature).
2. Export **`default`** and at least one of **`setup`** / **`setup_webserver`** from the package.
3. Enable in config, or set **`default = {"enabled": True}`** and omit YAML.

```yaml
extensions:
  hello:
    enabled: true
```

Config keys match folder names; **`my_ext`** and **`my-ext`** are equivalent ([Configuration](configuration.md)).

### Zip installs

Drop **`something.zip`** into **`src/extensions/`**. Botkit extracts it on startup and removes the zip. Useful for shipping extensions without unpacking manually.

---

## Required exports

| Export | Required | Purpose |
|--------|----------|---------|
| **`default`** | Yes | Must include **`enabled: bool`**. Default settings when YAML has no block for this extension. |
| **`setup`** | One of `setup` / `setup_webserver` | Register cogs, listeners, slash commands (`use.bot`) |
| **`setup_webserver`** | One of `setup` / `setup_webserver` | Register FastAPI routes (`use.backend`) |
| **`on_startup`** | No | Async hook before Discord connects; do not call Discord APIs that need a logged-in bot |

Hook functions only receive arguments you declare:

```python
def setup(bot, config): ...           # bot + config
def setup(bot): ...                   # bot only
def setup_webserver(app, bot, config): ...
async def on_startup(bot, config): ...
```

---

## Minimal bot-only extension

```
src/extensions/hello/
  __init__.py
  main.py
```

```python
# __init__.py
from .main import default, setup

__all__ = ["default", "setup"]
```

```python
# main.py
import discord
from discord.ext import commands

from src import custom


class HelloCog(commands.Cog):
    def __init__(self, bot: custom.Bot) -> None:
        self.bot = bot

    @discord.slash_command(name="hello", description="Say hello")
    async def hello(self, ctx: discord.ApplicationContext) -> None:
        await ctx.respond(f"Hello, {ctx.author.name}!")


def setup(bot: custom.Bot) -> None:
    bot.add_cog(HelloCog(bot))


default = {"enabled": True}
```

---

## Bot + HTTP extension

Discord command and health route (pattern from the bundled **ping** extension):

```python
import discord
from discord.ext import bridge, commands
from fastapi import FastAPI

from src import custom
from src.log import logger

default = {"enabled": True}


class BridgePing(commands.Cog):
    def __init__(self, bot: custom.Bot) -> None:
        self.bot = bot

    @bridge.bridge_command()
    async def ping(self, ctx: custom.Context, *, ephemeral: bool = False) -> None:
        await ctx.defer(ephemeral=ephemeral)
        await ctx.respond(f"Pong! {round(self.bot.latency * 1000)}ms", ephemeral=ephemeral)


def setup(bot: custom.Bot) -> None:
    bot.add_cog(BridgePing(bot))


def setup_webserver(app: FastAPI, bot: discord.Bot) -> None:
    @app.get("/ping")
    async def ping_route() -> dict[str, str]:
        if not bot.user:
            return {"message": "Bot is offline"}
        return {"message": f"{bot.user.name} is online"}


async def on_startup(config: dict[str, object]) -> None:
    logger.info("Ping extension started")
```

Set **`use.bot: true`** for the cog and **`use.backend: true`** for the route. With both enabled, the same **`bot`** instance is shared.

---

## Reading extension config

YAML under **`extensions.<name>`** is passed as **`config`**:

```python
def setup(bot: custom.Bot, config: dict[str, object]) -> None:
    url = config.get("webhook_url")
    if not url:
        logger.warning("my_ext: set extensions.my_ext.webhook_url in config")
        return
    bot.add_cog(MyCog(bot, str(url)))


default = {
    "enabled": False,
    "webhook_url": "",
}
```

Config keys are lowercase. Strings from **`translations.yml`** appear as **`config["translations"]`** — see [Internationalization](i18n.md).

---

## Translations

Optional **`translations.yml`** next to the extension, or **`src/translations/<name>.yml`**.

Without it, the extension still loads; you just won't get localized command names or **`ctx.translations`**. See [Internationalization](i18n.md).

---

## Patch files (`patch.py`)

Optional **`patch.py`** with a **`patch()`** function, run **before** the rest of the bot starts, only when the extension is enabled. Use rarely — for global behavior that must run early (for example error handling hooks).

```python
def patch() -> None:
    ...
```

Prefer normal extension code when you can.

---

## Common mistakes

| Problem | Fix |
|---------|-----|
| Extension not loading | Check **`enabled: true`** in YAML or **`default`** |
| `setup` never called | Set **`use.bot: true`** |
| Routes missing | Set **`use.backend: true`** and implement **`setup_webserver`** |
| Import error on startup | Fix Python errors in the extension package; check logs |
| Missing `default` or `enabled` | Add **`default = {"enabled": True}`** (or `False`) |

---

## Logging

Use Botkit's logger — not **`print()`**:

```python
from src.log import logger

log = logger.getChild("hello")

def setup(bot: custom.Bot) -> None:
    log.info("Loading hello extension")
    bot.add_cog(HelloCog(bot))
```

Levels respect **`logging.level`** in config ([Configuration](configuration.md)):

- **`DEBUG`** — detailed tracing
- **`INFO`** — startup, successful operations
- **`WARNING`** — missing config, degraded behavior
- **`ERROR`** / **`CRITICAL`** — failures

Log files are written when **`logging.file: true`**.

---

## Layout tips

- One feature per folder; split large extensions into **`commands.py`**, **`views.py`**, etc.
- Re-export **`setup`**, **`default`**, and optional hooks from **`__init__.py`**.
- Document extension-specific config in a local **`readme.md`**.

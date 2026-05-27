<!--
SPDX-License-Identifier: MIT
Copyright: 2024-2026 NiceBots.xyz
-->
# Getting started

## Prerequisites

- **Python 3.12** (Botkit pins `requires-python` to 3.12)
- **[PDM](https://pdm-project.org/latest/)** for installs and scripts
- A Discord application and bot token from the [Discord Developer Portal](https://discord.com/developers/applications)

## Install

```bash
git clone https://github.com/nicebots-xyz/botkit.git
cd botkit
pdm install
```

## Configuration file

Create **`config.yaml`** or **`config.yml`** in the project root (both names are supported; `config.yaml` is checked first). Start from `config.example.yaml` and set at least:

```yaml
bot:
  token: "your-bot-token"
  slash:
    enabled: true
use:
  bot: true
  backend: false
```

!!! warning "Secrets"
    Never commit real tokens. `config.yml` / `config.yaml` are gitignored by default.

## Run the bot

```bash
pdm run start
```

Botkit loads logging, runs any enabled extension patches, then starts Discord and/or the backend according to your config.

## Your first extension

1. Create a directory: `src/extensions/hello/`
2. Add `__init__.py` (can be empty or re-export from `main`).
3. Add `main.py` with the contract described in [Extensions](extensions.md).

Minimal example:

```python
# src/extensions/hello/main.py
import discord
from discord.ext import commands


class HelloCog(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @discord.slash_command(name="hello", description="Say hello")
    async def hello(self, ctx: discord.ApplicationContext) -> None:
        await ctx.respond(f"Hello, {ctx.author.name}!")


def setup(bot: discord.Bot) -> None:
    bot.add_cog(HelloCog(bot))


default = {"enabled": True}
```

If the extension folder is missing from `extensions:` in YAML, Botkit still discovers the package; missing keys fall back to the module’s **`default`** dict (see [Configuration](configuration.md)).

## Next steps

- [Configuration](configuration.md) — env vars, `use.bot` / `use.backend`, cache, REST mode
- [Extensions](extensions.md) — `setup_webserver`, `on_startup`, validation rules
- [Internationalization](i18n.md) — optional `translations.yml`

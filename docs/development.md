<!--
SPDX-License-Identifier: MIT
Copyright: 2024-2026 NiceBots.xyz
-->
# Development

This page is for **building your bot on top of Botkit** — local workflow, quality checks, and tooling shipped with the template. It is not about contributing changes back to the Botkit repository (see [Contributing](contributing.md) for that).

## Day-to-day commands

| Command | Purpose |
|---------|---------|
| `pdm run start` | Run the bot / backend (`python src`) |
| `pdm run format` | Format Python with Ruff |
| `pdm run lint` | Lint with Ruff (autofix where possible) |
| `pdm run tests` | Run pytest (`tests/`) |
| `pdm run typecheck` | Run basedpyright on the project |

Install dev dependencies once:

```bash
pdm install -d
```

You can drop these scripts entirely in a fork, swap Ruff for another formatter, or adopt your own commit conventions — Botkit does not enforce a workflow on downstream projects.

## Dependency cooldown

`pyproject.toml` sets a 7-day dependency cooldown:

```toml
[tool.pdm.resolution]
exclude-newer = "7d"
```

PDM never resolves a release younger than 7 days, which leaves time for a compromised or broken release to be yanked before it reaches `pdm.lock`. With a cooldown set, `pdm lock` re-resolves every package, so prefer `pdm add <pkg>` / `pdm update <pkg>` for targeted changes and `pdm lock --refresh` to only refresh hashes.

To take a release early (e.g. a security fix), exempt that package:

```toml
[tool.pdm.resolution.exclude-newer-override]
some-package = false
```

## Project layout for your code

| Location | Put your… |
|----------|-----------|
| `src/extensions/<name>/` | Features (cogs, listeners, HTTP routes) |
| `src/database/models/` | Tortoise models when `db` is enabled |
| `config.yaml` | Bot token, enabled extensions, runtime flags |
| `src/custom/` | Subclass `CustomBot` / contexts if you need global behavior |

Keep secrets in config or env, not in source.

## Tests

The template includes a small **`tests/`** suite as examples. Grow it as you add extensions. Run before deploy:

```bash
pdm run tests
```

## Type checking

Botkit uses **basedpyright** with project settings in `pyproject.toml`. Your extensions benefit from typing `bot: custom.Bot` and `ctx: custom.Context` for accurate checking.

## Config and deploy ergonomics

- **`pdm run convert-config`** — YAML ↔ `BOTKIT__` env (see [Scripts](scripts.md)).
- **`Dockerfile`** — production image without PDM in the runtime layer (see [Deployment](deployment.md)).

## Documentation for your bot

This site documents **Botkit**. Document your own commands and extension options in extension `readme.md` files, a `/help` implementation, or your project's external docs — whatever fits your bot.

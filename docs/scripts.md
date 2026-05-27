<!--
SPDX-License-Identifier: MIT
Copyright: 2024-2026 NiceBots.xyz
-->
# Scripts

PDM scripts are defined in `pyproject.toml` under `[tool.pdm.scripts]`.

## `pdm run start`

Runs **`python src`** — the main bot / backend entry (see [Runtime](runtime.md)).

## `pdm run convert-config`

**`scripts.convert_config`** converts between YAML and dotenv-style **`BOTKIT__`** environment files.

Common flags:

| Flag | Meaning |
|------|---------|
| `-i` / `--input` | Input path |
| `--input-format` | `yaml`, `yml`, or `env` |
| `--output` | Output path |
| `--output-format` | `yaml`, `yml`, or `env` |
| `--terminal` | Print env lines to stdout instead of writing a file |

Default behavior (no args) looks for `config.yaml` / `config.yml` and writes `.env` when safe; see `scripts/convert_config/` for interactive overwrite prompts.

## `pdm run check-listings`

Dev-only helper to scrape selected bot listing sites and compare descriptions to `description.md`. Requires **dev dependencies**, **Chrome**, and a root **`listings.yml`**. See `scripts/check_listings/` and inline comments in `readme.md` for the expected file shapes.

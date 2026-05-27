<!--
SPDX-License-Identifier: MIT
Copyright: 2024-2026 NiceBots.xyz
-->
# Deployment

## Docker

The included **`Dockerfile`** is multi-stage:

1. **Build stage** — PDM exports production dependencies to **`requirements.txt`** from `pyproject.toml` / `pdm.lock`.
2. **Runtime stage** — `pip install -r requirements.txt`, copy **`src/`** and **`LICENSE`**, run as non-root user **`appuser`**.

Default command:

```dockerfile
CMD ["python", "src"]
```

The image does **not** bake in `config.yaml`. Provide configuration at runtime:

- Mount **`config.yml`** / **`config.yaml`**, or
- Inject **`BOTKIT__…`** environment variables (see [Configuration](configuration.md))

Generate env lines from a local YAML file before deploy:

```bash
pdm run convert-config -i config.yaml --terminal
```

Process layout (`use`, cache, REST mode) is covered in [Configuration](configuration.md#process-layout).

## Environment-first deploys

Platforms without persistent volumes (Docker Swarm, some PaaS) often prefer env-only config. Merge order means env overrides file — you can ship a minimal file plus secrets as env vars.

Required minimum:

```env
BOTKIT__bot__token=…
BOTKIT__use__bot=true
```

## Health and observability

- Use extension HTTP routes (e.g. bundled **`/ping`** when ping's backend is enabled) or your own `setup_webserver` routes for load balancer checks.
- Enable **`logging.file: true`** and mount **`logging.directory`** if you need log persistence on disk.
- **Sentry** can be integrated in extensions (bundled **nice-errors** patches error paths when enabled).

## What ships in the image

Production export includes runtime Python dependencies only — not dev tools (pytest, ruff, zensical). Build and test in CI or locally before pushing the image.

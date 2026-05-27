<!--
SPDX-License-Identifier: MIT
Copyright: 2024-2026 NiceBots.xyz
-->
# Database (optional)

Botkit works without a database. Enable **`db`** when you need PostgreSQL persistence with **Tortoise ORM** and **Aerich** migrations.

## Enable

```yaml
db:
  enabled: true
  url: "postgres://user:pass@host:5432/dbname"
  params: {}
  extra_apps: {}
```

| Key | Default | Role |
|-----|---------|------|
| `enabled` | `false` | Turn on database at startup |
| `url` | `""` | PostgreSQL connection URL |
| `params` | optional | Extra query parameters (see SSL) |
| `extra_apps` | `{}` | Additional databases / model packages |

On each start, Botkit applies pending **migrations** automatically, then connects. If migration or connection fails, the bot does not start.

## SSL

For providers that require verified TLS, set **`ssl: true`** under **`params`** and place the CA certificate at:

```
.postgres/root.crt
```

(project root)

## Models

Define models in **`src/database/models/`** and extend the included stubs (`Guild`, `User`, etc.) as needed.

Create migrations during development with the **Aerich CLI** (configured in **`pyproject.toml`**). Botkit only **applies** migrations at runtime — it does not generate new migration files for you.

## Multiple databases

Register extra Tortoise apps with different URLs:

```yaml
db:
  enabled: true
  url: "postgres://user:pass@localhost:5432/main"
  extra_apps:
    analytics:
      url: "postgres://user:pass@localhost:5432/analytics"
      models:
        - my_project.analytics.models
```

## Optional field types

For typed JSON columns or UUID v6+ primary keys, see **[tortoise-extensions](https://docs.nicebots.xyz/tortoise-extensions/)** — add it as a dependency and use its fields in your models like any other library.

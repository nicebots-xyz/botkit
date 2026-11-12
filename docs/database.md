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
| `s3` | optional | S3 storage for the main app (see S3) |
| `s3_storages` | `{}` | Extra named S3 storages |

On each start, Botkit applies pending **migrations** automatically, then connects. If migration or connection fails, the bot does not start.

## SSL

For providers that require verified TLS, set **`ssl: true`** under **`params`** and place the CA certificate at:

```
.postgres/root.crt
```

(project root)

Each entry in **`extra_apps`** can set its own **`params.ssl`** to override this per connection. When it is omitted, the connection follows the top-level **`params.ssl`**.

```yaml
db:
  url: "postgres://user:pass@haproxy:5000/main"
  extra_apps:
    analytics:
      url: "postgres://user:pass@other-host:5432/analytics"
      params:
        ssl: true
```

## S3

Columns declared with **`S3Field`** from [tortoise-extensions](https://docs.nicebots.xyz/tortoise-extensions/) store their content in S3-compatible storage. Each Tortoise app gets its own storage: the main app uses **`db.s3`**, and each entry in **`extra_apps`** uses its own **`s3`**, falling back to **`db.s3`**. Fields can target a named storage from **`s3_storages`** with `S3Field(storage="name")`.

```yaml
db:
  s3:
    endpoint: "s3.example.com"
    bucket: "main"
    access_key: "..."
    secret_key: "..."
  extra_apps:
    analytics:
      s3:
        endpoint: "minio:9000"
        bucket: "analytics"
        access_key: "..."
        secret_key: "..."
        ssl: false
  s3_storages:
    cdn:
      endpoint: "cdn.example.com"
      bucket: "cdn"
      access_key: "..."
      secret_key: "..."
```

| Key | Default | Role |
|-----|---------|------|
| `endpoint` | required | Host and optional port, without scheme |
| `bucket` | required | Bucket holding the objects |
| `access_key` / `secret_key` | required | Credentials |
| `region` | optional | Signing region |
| `ssl` | `true` | `https` when `true`, plain `http` when `false` |

Secrets can come from the environment, e.g. **`BOTKIT__DB__S3__SECRET_KEY`**.

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

For typed JSON columns, UUID v6+ primary keys or S3 columns, see **[tortoise-extensions](https://docs.nicebots.xyz/tortoise-extensions/)** — add it as a dependency and use its fields in your models like any other library.

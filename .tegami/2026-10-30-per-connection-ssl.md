---
packages:
  botkit: minor
---

### Per connection database SSL

Each `db.extra_apps` entry can set `params.ssl` to enable or disable verified TLS for its own connection. Entries without it keep following the top-level `db.params.ssl`.

---
packages:
  botkit: patch
---

### Bots built on Botkit need no configuration

Botkit's release line becomes read only as soon as a repository adds a release line of its own, so the optional `scripts/tegami.local.mts` file is gone. Merging Botkit into a bot no longer conflicts on release configuration.

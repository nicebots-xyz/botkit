---
packages:
  botkit: patch
---

### CI checks out submodules and tests run without a database

The quality and Docker workflows check out git submodules, using a `PAT` secret when one is set, so bots built on Botkit can keep the workflows unchanged. Tests turn the database off, and a disabled database no longer loads an SSL certificate.

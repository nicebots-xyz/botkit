---
packages:
  botkit: patch
---

### Separate Renovate pull requests per ecosystem

Non-major updates are grouped per ecosystem, with Python and JavaScript dependencies in separate weekly pull requests, and Python interpreter upgrades leave the group, so a failing interpreter bump no longer blocks every other update. Changelog entries of dependency updates list every package with both versions. Cooldowns, titles and lock file maintenance now come from the shared Renovate preset, and the licensor release installed by the quality checks is tracked alongside its action.

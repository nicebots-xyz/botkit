---
packages:
  botkit: patch
---

### Separate Renovate pull requests per ecosystem and lock file

Non-major updates are grouped per ecosystem, with Python and JavaScript dependencies in separate weekly pull requests whose titles name the packages. Python interpreter upgrades leave the group and get their own pull request again, so a failing interpreter bump no longer blocks every other update. `pdm.lock` and `pnpm-lock.yaml` are maintained in separate pull requests, and changelog entries of dependency updates list every package with both versions.

---
packages:
  botkit: minor
---

## Changelog entries for Renovate dependency updates

Renovate pull requests that update a runtime dependency (`fix(deps): ...`) now get a `patch` changelog entry automatically, committed by the fixer GitHub App. Dev tooling, GitHub Actions and lock file maintenance are skipped.

Setup is described in the "Dependency updates" section of the releases documentation: install the fixer GitHub App on the repository and add a `fixer` environment with `FIXER_APP_CLIENT_ID` and `FIXER_APP_PRIVATE_KEY`.

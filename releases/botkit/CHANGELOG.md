## botkit@0.2.1

### Upgrade nicebots-xyz/licensor action to v0.1.1

## botkit@0.2.0

### Bots built on Botkit need no configuration

Botkit's release line becomes read only as soon as a repository adds a release line of its own, so the optional `scripts/tegami.local.mts` file is gone. Merging Botkit into a bot no longer conflicts on release configuration.

### Changelog entries for every Renovate dependency update

Renovate dependency update pull requests now get a `patch` changelog entry whatever they update, including dev tooling, GitHub Actions and Docker. Only lock file maintenance is skipped.

### Changelog entries for Renovate dependency updates

Renovate pull requests that update a runtime dependency (`fix(deps): ...`) now get a `patch` changelog entry automatically, committed by the fixer GitHub App. Dev tooling, GitHub Actions and lock file maintenance are skipped.

Setup is described in the "Dependency updates" section of the releases documentation: install the fixer GitHub App on the repository and add a `fixer` environment with `FIXER_APP_CLIENT_ID` and `FIXER_APP_PRIVATE_KEY`.

### No release preview comment on bot pull requests

Pull requests opened by bots, such as Renovate and the Version Packages pull request, no longer get the Tegami preview comment.

### Version Packages pull request passes the repository checks

The pull request is titled `chore(release): version packages` to satisfy the semantic title check, and the generated `releases/*/CHANGELOG.md` files are exempt from the license header check.

### Upgrade docker/login-action action to v4.7.0



### Upgrade pnpm to v12



### Upgrade pnpm/action-setup digest to ea17c68

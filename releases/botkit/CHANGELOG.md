## botkit@0.3.1

### Spend fewer CI minutes on pull requests

## botkit@0.3.0

### Per connection database SSL

Each `db.extra_apps` entry can set `params.ssl` to enable or disable verified TLS for its own connection. Entries without it keep following the top-level `db.params.ssl`.

### Replace autofix.ci with NiceBots Autofixer



### Weekly cleanup of old container images



### Remove certifi cooldown bypass



### S3 storages for database models

`db.s3` and `db.extra_apps.<app>.s3` configure S3-compatible storages for `S3Field` columns from `tortoise-extensions`, with SSL toggled per storage. Setting `type: memory` or `type: local` swaps a storage for an in-memory or on-disk one for tests and local development. Extra apps without `s3` follow the top-level `db.s3`.

### Upgrade amannn/action-semantic-pull-request action to v6.1.2



### Upgrade docker/login-action action to v4.8.0



### Upgrade nicebots-xyz/licensor action to v0.1.2



### Upgrade pnpm to v12.18.0



### Upgrade pnpm/action-setup action to v6.1.1

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

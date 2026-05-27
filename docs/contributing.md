<!--
SPDX-License-Identifier: MIT
Copyright: 2024-2026 NiceBots.xyz
-->
# Contributing

This page is for **changes to the Botkit template repository** — framework code, bundled extensions, docs site, and CI. If you are only building a bot on a fork, you do not need to follow these conventions unless you plan to open a pull request here.

## Workflow

1. Open an issue for larger design changes or reproducible bugs.
2. Branch from **`dev`** (CI target for pull requests).
3. Keep PRs focused; match existing style (Ruff, typing, module layout).

## Commit messages

Use **Conventional Commits** ([spec](https://www.conventionalcommits.org/)):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Common types:

| Type | Use for |
|------|---------|
| `feat` | New framework capability or extension contract change |
| `fix` | Bug fix in core startup, config, loader, etc. |
| `docs` | Documentation under `docs/` or readme |
| `refactor` | Code change without behavior change |
| `test` | Tests only |
| `chore` | Tooling, CI, dependencies |

Examples:

```
feat(loader): resolve extension config keys with hyphen aliases
fix(start): reject bot.rest and use.backend in the same process
docs(configuration): document env coercion and cache defaults
```

## Quality gate

Before opening a PR:

```bash
pdm install -dG docs
pdm run format
pdm run lint
pdm run tests
pdm run typecheck
pdm run docs:build
```

CI (`.github/workflows/quality.yaml`) runs format check, lint, tests, and **docs build** on a matrix.

## Documentation site

Botkit docs are built with **Zensical** (`zensical.toml`, sources in **`docs/`**).

| Command | Purpose |
|---------|---------|
| `pdm run docs:dev` | Local preview with live reload |
| `pdm run docs:build` | Static site → **`site/`** (gitignored) |
| `pdm run docs:preview` | Serve `site/` on port 8000 after a build |

Install docs dependencies:

```bash
pdm install -dG docs
```

When you change startup behavior, config models, or extension contracts, update the matching page under **`docs/`** and confirm **`pdm run docs:build`** succeeds.

Published URL: [docs.nicebots.xyz/botkit](https://docs.nicebots.xyz/botkit/). On **`nicebots-xyz/botkit`**, CI builds docs on every run and publishes to GitHub Pages on push to the repository default branch (`.github/workflows/docs.yaml`, invoked from `CI-CD.yaml`).

## Copyright headers

Sources use **[Licensor](https://github.com/nicebots-xyz/licensor)** (`licensor-config.yaml`).

```bash
licensor check * --ignore ".*"
licensor add * --ignore ".*"
```

New files should include the MIT header block used elsewhere in the repo.

## Pull request checklist

- [ ] Behavior change covered by tests when practical
- [ ] `docs/` updated for user-visible contract changes
- [ ] `pdm run docs:build` passes
- [ ] Conventional Commit message on the PR branch

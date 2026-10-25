<!--
SPDX-License-Identifier: MIT
Copyright: 2024-2026 NiceBots.xyz
-->
# Changelogs and releases

Botkit and the bots built on it keep their changelogs in one place, with **[Tegami](https://github.com/fuma-nama/tegami)**.
Every pull request that changes behavior adds a small markdown file. CI compiles them into versions, changelogs, tags and GitHub releases.

## Release lines

A **release line** is something with its own version and changelog. It is a directory under `releases/`.

| Path | Contents |
|------|----------|
| `releases/<name>/VERSION` | Current version of the line |
| `releases/<name>/CHANGELOG.md` | Generated, never edited by hand |

| Repository | Release lines | Git tags |
|------------|---------------|----------|
| `nicebots-xyz/botkit` | `botkit` | `botkit@0.2.0` |
| A bot that merges Botkit back | `botkit` (arrives through merges, read only) and its own, for example `mybot` | `mybot@1.4.0` |

Entries are tagged with the line they belong to, so Botkit changes and bot changes never mix up, even though they sit in the same `.tegami/` folder.

## Adding an entry to a pull request

```bash
pnpm install
pnpm tegami
```

Or create `.tegami/<anything>.md` by hand:

```md
---
packages:
  botkit: minor
---

## Add a shared rate limiter for extensions

Extensions can now call `RateLimiter` instead of rolling their own.
```

| Frontmatter | Meaning |
|-------------|---------|
| `botkit: minor` | The bump for that line: `major`, `minor` or `patch` |
| `packages: [botkit]` | Bump inferred from the headings: `#` major, `##` minor, `###` patch |

The headings are the release notes. A pull request comment shows the pending bumps and links to the page that creates an entry.

## What CI does

| Event | Result |
|-------|--------|
| Pull request | Release preview comment |
| Push to the default branch with pending entries | A **Version Packages** pull request bumps `VERSION`, writes `CHANGELOG.md` and removes the consumed entries |
| Version Packages pull request merged | Tags `<name>@<version>` and a GitHub release with the notes |

Workflows: `release.yaml`, `tegami_pr.yaml`, `tegami_pr_comment.yaml`.

!!! note
    The Version Packages pull request is opened with `GITHUB_TOKEN`, so GitHub does not start other workflows on it.
    If you require status checks before merging, pass a personal access token or GitHub App token as `GITHUB_TOKEN` in `release.yaml`.

## Using it in a bot built on Botkit

This is for a bot repository that started from Botkit and keeps pulling Botkit changes into it.
Botkit's setup comes along with those merges, so only your own release line needs adding.
No file that Botkit ships has to be edited. As soon as `releases/` holds a line besides `botkit`, `botkit` becomes read only: it is never versioned in your repository and only changes through merges.

### One time setup

1. Create your line. Pick a short name, it becomes the tag prefix (`mybot@1.0.0`).

    ```bash
    mkdir releases/mybot
    echo 0.1.0 > releases/mybot/VERSION
    ```

2. In the repository settings, open **Settings, Actions, General** and enable **Allow GitHub Actions to create and approve pull requests**.
   The Version Packages pull request cannot be opened without it.

3. Install the tooling once.

    ```bash
    pnpm install
    ```

### Day to day

Add an entry for `mybot` to every pull request that changes behavior.

```md
---
packages:
  mybot: minor
---

## Join Guard

New screening for joining members.
```

When pull requests with entries reach the default branch, `release.yaml` opens the Version Packages pull request.
Merging it bumps `releases/mybot/VERSION`, updates `releases/mybot/CHANGELOG.md`, then tags `mybot@<version>` and creates the GitHub release.

### Pulling in Botkit changes

```bash
git remote add botkit https://github.com/nicebots-xyz/botkit.git
git fetch botkit
git merge botkit/dev
```

| Thing | Behavior |
|-------|----------|
| `releases/botkit/` | Updated only by merges, so it always shows which Botkit release you are on |
| `releases/botkit/CHANGELOG.md` | Everything that changed in Botkit, ready to read before you merge the next release |
| `releases/mybot/` | Versioned from your own entries |
| `.tegami/*.md` entries for `botkit` that arrive through a merge | Left in place, Botkit consumes them in its own repository |
| Tegami warning `no detected packages from name "botkit"` | Expected while such an entry is pending |

To list what changed in Botkit since your last merge, compare `releases/botkit/CHANGELOG.md` before and after the merge.

If Botkit's own change affects your bot, mention it in an entry for `mybot` as well. The two changelogs stay separate on purpose.

### Rules for shared files

Do not edit these in a bot repository, they belong to Botkit and merges would conflict.

- `scripts/tegami.mts`
- `scripts/tegami-releases.mts`
- `.github/workflows/release.yaml`
- `.github/workflows/tegami_pr.yaml`
- `.github/workflows/tegami_pr_comment.yaml`
- `.github/workflows/tegami_renovate.yaml`

## Dependency updates

Renovate pull requests get a `patch` changelog entry automatically: runtime dependencies, dev tooling, GitHub Actions and Docker updates alike.
Lock file maintenance does not, it only changes transitive versions.

| Step | Who |
|------|-----|
| `scripts/tegami-renovate.mts` writes `.tegami/renovate-<branch>.md`, a `patch` for your release line | `tegami_renovate.yaml`, in a read only job |
| The entry is committed to the Renovate branch | [`nicebots-xyz/fixer`](https://github.com/nicebots-xyz/fixer), with its GitHub App, so CI runs again |

Fixer refuses patches that touch `.github/`. That only concerns what the entry job changes, which is a single file in `.tegami/`, so Renovate pull requests that update workflows are not affected.

The entry goes to the only release line your repository owns, that is every line except `botkit` once you have your own. With several lines of your own, the script skips and you add entries by hand.

Setup is the one [fixer](https://github.com/nicebots-xyz/fixer#setup) needs: the GitHub App installed on the repository, and a `fixer` environment holding `FIXER_APP_CLIENT_ID` and `FIXER_APP_PRIVATE_KEY`.
Without it, the `push` job fails on Renovate dependency update pull requests.

## Requirements

Node.js 24 and pnpm, only for releases. Running a bot does not need either.

Do not edit `releases/*/VERSION`, `releases/*/CHANGELOG.md` or `.tegami/publish-lock.yaml` by hand.

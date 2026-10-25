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

## Setting up a bot that merges Botkit back

Merging Botkit gives you the whole setup. Add your own line, and tell Tegami that `botkit` belongs to someone else.

1. Create your line. Pick a short name, it becomes the tag prefix.

    ```bash
    mkdir releases/mybot
    echo 0.1.0 > releases/mybot/VERSION
    ```

2. Create `scripts/tegami.local.mts`. Only your fork has this file, so merging Botkit never conflicts on it.

    ```ts
    export default {
      ignore: ["botkit"],
    };
    ```

3. Write entries for `mybot` in your pull requests.

   ```md
   ---
   packages:
     mybot: minor
   ---

   ## Join Guard
   ```

Your fork now behaves like this.

| Thing | Behavior |
|-------|----------|
| `.tegami/*.md` entries for `botkit` that arrive through a merge | Left in place, Botkit consumes them in its own repository |
| `releases/botkit/` | Updated only by merges, so it always shows which Botkit release you are on |
| `releases/mybot/` | Versioned from your entries |
| Tegami warning `no detected packages from name "botkit"` | Expected while such an entry is pending |

## Requirements

Node.js 24 and pnpm, only for releases. Running a bot does not need either.

Do not edit `releases/*/VERSION`, `releases/*/CHANGELOG.md` or `.tegami/publish-lock.yaml` by hand.

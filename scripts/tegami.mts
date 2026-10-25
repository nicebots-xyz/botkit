// SPDX-License-Identifier: MIT
// Copyright: 2024-2026 NiceBots.xyz

import { access } from "node:fs/promises";
import { tegami } from "tegami";
import { runCli } from "tegami/cli";
import { github } from "tegami/plugins/github";
import { releases } from "./tegami-releases.mts";

/**
 * Per-repository overrides, loaded from `scripts/tegami.local.mts` when it exists.
 *
 * Forks of Botkit should put their settings there instead of editing this file,
 * so that merging upstream never conflicts on it.
 */
interface LocalConfig {
  /** Release lines owned by another repository (e.g. `botkit` in a fork), they are never versioned here. */
  ignore?: string[];
}

const localPath = new URL("./tegami.local.mts", import.meta.url);
const local: LocalConfig = await access(localPath).then(
  async () => (await import(localPath.href)).default,
  () => ({}),
);

// The "Version Packages" pull request targets the branch being released. `pull_request` events check out
// a merge ref, so there it is the PR base. Both variables are set but empty on the other kind of event.
const base = process.env.GITHUB_BASE_REF || process.env.GITHUB_REF_NAME || "dev";

const paper = tegami({
  ignore: local.ignore,
  npm: { updateLockFile: false },
  plugins: [releases(), github({ versionPr: { base } })],
});

await runCli(paper);

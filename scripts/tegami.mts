// SPDX-License-Identifier: MIT
// Copyright: 2024-2026 NiceBots.xyz

import { tegami } from "tegami";
import { runCli } from "tegami/cli";
import { github } from "tegami/plugins/github";
import { foreignLines } from "./tegami-lines.mts";
import { releases } from "./tegami-releases.mts";

// The "Version Packages" pull request targets the branch being released. `pull_request` events check out
// a merge ref, so there it is the PR base. Both variables are set but empty on the other kind of event.
const base = process.env.GITHUB_BASE_REF || process.env.GITHUB_REF_NAME || "dev";

const paper = tegami({
  ignore: await foreignLines(),
  npm: { updateLockFile: false },
  plugins: [releases(), github({ versionPr: { base } })],
});

await runCli(paper);

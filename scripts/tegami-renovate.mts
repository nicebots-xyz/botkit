// SPDX-License-Identifier: MIT
// Copyright: 2024-2026 NiceBots.xyz

import { mkdir, writeFile } from "node:fs/promises";
import { loadLocalConfig, ownedLines } from "./tegami-local.mts";

/**
 * Writes a changelog entry for a Renovate pull request that updates a runtime dependency.
 *
 * Renovate titles runtime dependency updates `fix(deps): ...` and everything else (dev tooling, actions,
 * lock file maintenance) `chore(deps): ...`, only the former is worth a line in the changelog.
 * Meant to run in CI with the pull request title and branch in `PR_TITLE` and `PR_BRANCH`.
 */
const title = process.env.PR_TITLE?.trim() ?? "";
const branch = process.env.PR_BRANCH?.trim() ?? "";

const subject = /^fix\(deps\): (.+)$/.exec(title)?.[1];
if (!subject) {
  console.log(`"${title}" is not a runtime dependency update, no entry needed.`);
  process.exit(0);
}

const { ignore } = await loadLocalConfig();
const lines = await ownedLines(ignore);
const [line] = lines;
if (lines.length !== 1 || !line) {
  console.log(`Expected exactly one release line owned by this repository, found: ${lines.join(", ") || "none"}.`);
  process.exit(0);
}

const slug = branch.toLowerCase().replace(/[^a-z0-9.]+/g, "-").replace(/^-+|-+$/g, "");
if (!slug) throw new Error("PR_BRANCH is required.");

const heading = subject.charAt(0).toUpperCase() + subject.slice(1);
const content = `---\npackages:\n  ${line}: patch\n---\n\n### ${heading}\n`;

await mkdir(".tegami", { recursive: true });
await writeFile(`.tegami/${slug}.md`, content);
console.log(`Wrote .tegami/${slug}.md for "${line}".`);

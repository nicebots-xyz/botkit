// SPDX-License-Identifier: MIT
// Copyright: 2024-2026 NiceBots.xyz

import { mkdir, writeFile } from "node:fs/promises";
import { loadLocalConfig, ownedLines } from "./tegami-local.mts";

/**
 * Writes a changelog entry for a Renovate pull request.
 *
 * Every dependency update gets one (runtime dependencies, dev tooling, GitHub Actions...), except lock file
 * maintenance, which only churns transitive versions. Renovate titles them `<type>(deps): <subject>`.
 * Meant to run in CI with the pull request title and branch in `PR_TITLE` and `PR_BRANCH`.
 */
const title = process.env.PR_TITLE?.trim() ?? "";
const branch = process.env.PR_BRANCH?.trim() ?? "";

const subject = /^\w+\(deps[\w-]*\)!?: (.+)$/.exec(title)?.[1];
if (!subject || /lock ?file/i.test(subject)) {
  console.log(`"${title}" is not a dependency update that needs an entry.`);
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

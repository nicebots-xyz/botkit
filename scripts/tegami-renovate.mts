// SPDX-License-Identifier: MIT
// Copyright: 2024-2026 NiceBots.xyz

import { mkdir, writeFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";
import { ownedLines } from "./tegami-lines.mts";

/** One row of the table of updates Renovate puts at the top of its pull request body. */
export interface Upgrade {
  name: string;
  from: string;
  to: string;
}

/** Turns `[text](url)` links into their text and drops code spans and the `(source)` and `(changelog)` links. */
function plain(cell: string): string {
  return cell
    .replace(/\s*\(\[(?:source|changelog)\]\([^)]*\)\)/g, "")
    .replace(/!?\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replaceAll("`", "")
    .trim();
}

/**
 * Reads the updates from the `| Package | Change | ...` table of a Renovate pull request body.
 *
 * Rows that repeat a package and change already listed (one dependency used in several files) are kept once.
 */
export function parseUpgrades(body: string): Upgrade[] {
  const lines = body.split(/\r?\n/);
  const header = lines.findIndex((line) => /^\|\s*Package\s*\|/.test(line));
  if (header === -1) return [];

  const cells = (line: string): string[] => line.split("|").slice(1, -1).map((cell) => cell.trim());
  const columns = cells(lines[header] ?? "");
  const nameColumn = columns.indexOf("Package");
  const changeColumn = columns.indexOf("Change");
  if (changeColumn === -1) return [];

  const upgrades: Upgrade[] = [];
  const seen = new Set<string>();
  for (const line of lines.slice(header + 2)) {
    if (!line.startsWith("|")) break;

    const row = cells(line);
    const name = plain(row[nameColumn] ?? "");
    const [from, to] = plain(row[changeColumn] ?? "").split("→").map((side) => side.trim());
    if (!name || !from || !to) continue;

    const key = `${name} ${from} ${to}`;
    if (seen.has(key)) continue;
    seen.add(key);
    upgrades.push({ name, from, to });
  }

  return upgrades;
}

/**
 * Builds the changelog entry of a Renovate pull request, or `null` when it needs none.
 *
 * Every dependency update gets one (runtime dependencies, dev tooling, GitHub Actions...), except lock file
 * maintenance, which only churns transitive versions. Renovate titles them `<type>(deps): <subject>`. The entry lists
 * each upgrade with its versions, unless the title already says everything about a single one.
 */
export function entry(title: string, branch: string, body: string, line: string): string | null {
  const subject = /^\w+\(deps[\w-]*\)!?: (.+)$/.exec(title.trim())?.[1];
  if (!subject || /lock-file-maintenance/.test(branch) || /lock ?file/i.test(subject)) return null;

  const heading = subject.charAt(0).toUpperCase() + subject.slice(1);
  const upgrades = parseUpgrades(body);
  const [only] = upgrades;
  const selfExplanatory = upgrades.length === 1 && only !== undefined && heading.includes(only.to.replace(/^v/, ""));

  const list =
    upgrades.length === 0 || selfExplanatory
      ? ""
      : `\n${upgrades.map(({ name, from, to }) => `- \`${name}\`: \`${from}\` → \`${to}\``).join("\n")}\n`;

  return `---\npackages:\n  ${line}: patch\n---\n\n### ${heading}\n${list}`;
}

/**
 * Writes the changelog entry of the Renovate pull request described by `PR_TITLE`, `PR_BRANCH` and `PR_BODY`.
 *
 * Meant to run in CI, which reads the title and body of the pull request when the job runs: both change while a
 * grouped update gathers more packages.
 */
async function main(): Promise<void> {
  const title = process.env.PR_TITLE?.trim() ?? "";
  const branch = process.env.PR_BRANCH?.trim() ?? "";
  const body = process.env.PR_BODY ?? "";

  const lines = await ownedLines();
  const [line] = lines;
  if (lines.length !== 1 || !line) {
    console.log(`Expected exactly one release line owned by this repository, found: ${lines.join(", ") || "none"}.`);
    return;
  }

  const content = entry(title, branch, body, line);
  if (content === null) {
    console.log(`"${title}" is not a dependency update that needs an entry.`);
    return;
  }

  const slug = branch.toLowerCase().replace(/[^a-z0-9.]+/g, "-").replace(/^-+|-+$/g, "");
  if (!slug) throw new Error("PR_BRANCH is required.");

  await mkdir(".tegami", { recursive: true });
  await writeFile(`.tegami/${slug}.md`, content);
  console.log(`Wrote .tegami/${slug}.md for "${line}".`);
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? "").href) await main();

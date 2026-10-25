// SPDX-License-Identifier: MIT
// Copyright: 2024-2026 NiceBots.xyz

import { readdir } from "node:fs/promises";

/** The release line that Botkit itself versions. */
export const UPSTREAM_LINE = "botkit";

/** Every release line (`releases/<name>/`) present in the repository. */
export async function listLines(dir = "releases"): Promise<string[]> {
  const entries = await readdir(dir, { withFileTypes: true }).catch(() => []);

  return entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name);
}

/**
 * Release lines that belong to another repository, they are never versioned here.
 *
 * Botkit's own line becomes read only (it only changes through merges) as soon as a repository adds a line
 * of its own, so a bot built on Botkit needs no configuration and no edit to any shared file.
 */
export async function foreignLines(dir = "releases"): Promise<string[]> {
  const lines = await listLines(dir);

  return lines.length > 1 && lines.includes(UPSTREAM_LINE) ? [UPSTREAM_LINE] : [];
}

/** Release lines that this repository versions itself. */
export async function ownedLines(dir = "releases"): Promise<string[]> {
  const foreign = await foreignLines(dir);

  return (await listLines(dir)).filter((line) => !foreign.includes(line));
}

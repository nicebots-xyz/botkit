// SPDX-License-Identifier: MIT
// Copyright: 2024-2026 NiceBots.xyz

import { access, readdir } from "node:fs/promises";

/**
 * Per-repository overrides, loaded from `scripts/tegami.local.mts` when it exists.
 *
 * Forks of Botkit should put their settings there instead of editing the shared scripts,
 * so that merging upstream never conflicts on them.
 */
export interface LocalConfig {
  /** Release lines owned by another repository (e.g. `botkit` in a fork), they are never versioned here. */
  ignore?: string[];
}

export async function loadLocalConfig(): Promise<LocalConfig> {
  const localPath = new URL("./tegami.local.mts", import.meta.url);
  const exists = await access(localPath).then(
    () => true,
    () => false,
  );
  if (!exists) return {};

  return (await import(localPath.href)).default;
}

/** Release lines (`releases/<name>/`) that this repository versions itself. */
export async function ownedLines(ignore: string[] = [], dir = "releases"): Promise<string[]> {
  const entries = await readdir(dir, { withFileTypes: true }).catch(() => []);

  return entries
    .filter((entry) => entry.isDirectory() && !ignore.includes(entry.name))
    .map((entry) => entry.name);
}

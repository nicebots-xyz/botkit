// SPDX-License-Identifier: MIT
// Copyright: 2024-2026 NiceBots.xyz

import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { WorkspacePackage } from "tegami";
import type { TegamiPlugin } from "tegami";
import { GitTagPublishTask } from "tegami/plugins/git";

const VERSION_FILE = "VERSION";
const SEMVER = /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/;

/**
 * A release line backed by a `releases/<name>/VERSION` file.
 *
 * The version lives in a plain text file instead of `pyproject.toml`, so that forks of Botkit can
 * track their own version next to Botkit's without both fighting over the same line.
 * Its `CHANGELOG.md` is written by Tegami into the same directory.
 */
export class ReleasePackage extends WorkspacePackage {
  readonly manager = "release";
  readonly name: string;
  readonly path: string;
  private current: string;

  constructor(dir: string, version: string) {
    super();
    this.path = dir;
    this.name = path.basename(dir);
    this.current = version;
  }

  get version(): string {
    return this.current;
  }

  setVersion(version: string): void {
    this.current = version;
  }

  async write(): Promise<void> {
    await writeFile(path.join(this.path, VERSION_FILE), `${this.current}\n`);
  }
}

/** A release line is "published" by tagging it (`<name>@<version>`), the git plugin does the tagging. */
class ReleasePublishTask extends GitTagPublishTask<ReleasePackage> {}

export interface ReleasesPluginOptions {
  /**
   * Directory containing one sub-directory per release line, relative to the workspace root.
   *
   * @default "releases"
   */
  dir?: string;
}

/** Discovers every `<dir>/<name>/VERSION` as a package named `<name>`. */
export function releases({ dir = "releases" }: ReleasesPluginOptions = {}): TegamiPlugin {
  return {
    name: "releases",
    async resolve() {
      const root = path.resolve(this.cwd, dir);
      const entries = await readdir(root, { withFileTypes: true }).catch(() => []);

      for (const entry of entries) {
        if (!entry.isDirectory()) continue;

        const packagePath = path.join(root, entry.name);
        const version = await readFile(path.join(packagePath, VERSION_FILE), "utf8")
          .then((content) => content.trim())
          .catch(() => undefined);
        if (version === undefined) continue;
        if (!SEMVER.test(version)) {
          throw new Error(`[releases] "${entry.name}/${VERSION_FILE}" is not a valid version: "${version}"`);
        }

        this.graph.add(new ReleasePackage(packagePath, version));
      }
    },
    async applyDraft(draft) {
      // Entries that target no release line of this repository (e.g. Botkit's own entries that
      // arrived in a fork through a merge) must stay untouched, upstream consumes them itself.
      for (const entry of draft.getChangelogs()) {
        const local = [...entry.packages.keys()].some((name) => this.graph.getByName(name).length > 0);
        if (!local) draft.deleteChangelog(entry.id);
      }

      await Promise.all(
        this.graph.getPackages().map(async (pkg) => {
          if (!(pkg instanceof ReleasePackage)) return;

          const bumped = draft.getPackageDraft(pkg.id)?.bumpVersion(pkg);
          if (!bumped) return;

          pkg.setVersion(bumped);
          await pkg.write();
        }),
      );
    },
    publishPreflight({ pkg }) {
      if (!(pkg instanceof ReleasePackage)) return;
      return { shouldPublish: true };
    },
    publishTasks({ plan }) {
      return plan
        .getPackagesToPublish()
        .map((pkg) => pkg instanceof ReleasePackage && new ReleasePublishTask(pkg));
    },
  };
}

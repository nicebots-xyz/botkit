# Copyright (c) NiceBots
# SPDX-License-Identifier: MIT

from pathlib import Path
from typing import Any

import yaml
from dotenv import dotenv_values


def yaml_to_env(yaml_path: Path, output_path: Path | None = None) -> None:
    with yaml_path.open("r", encoding="utf-8") as yaml_file:
        config = yaml.safe_load(yaml_file)

    env_lines = []

    def recurse_dict(d: dict[Any, Any], prefix: str = "") -> None:
        for key, val in d.items():
            if isinstance(val, dict):
                recurse_dict(val, f"{prefix}{key.lower()}__")
            else:
                # Convert boolean values to lowercase strings
                env_value = str(val).lower() if isinstance(val, bool) else val
                env_lines.append(f"BOTKIT__{prefix}{key.lower()}={env_value}")

    recurse_dict(config)

    if output_path:
        with output_path.open("w", encoding="utf-8") as env_file:
            env_file.write("\n".join(env_lines) + "\n")  # Add final newline
    else:
        print("\n".join(env_lines))


def env_to_yaml(env_path: Path, output_path: Path | None = None) -> None:
    env_config = dotenv_values(env_path)
    yaml_config = {}

    for key, val in env_config.items():
        if not key.startswith("BOTKIT__"):
            continue
        parts = key[8:].split("__")  # Remove BOTKIT__ prefix
        current = yaml_config
        for part in parts[:-1]:
            current = current.setdefault(part.lower(), {})

        # Convert string boolean values to actual booleans
        yaml_value = val
        if val.lower() == "true":
            yaml_value = True
        elif val.lower() == "false":
            yaml_value = False

        current[parts[-1].lower()] = yaml_value

    if output_path:
        with output_path.open("w", encoding="utf-8") as yaml_file:
            yaml.safe_dump(yaml_config, yaml_file)  # Use safe_dump to avoid string quotes
    else:
        print(yaml.safe_dump(yaml_config))

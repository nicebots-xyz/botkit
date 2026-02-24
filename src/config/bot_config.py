# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

import contextlib
import os
from collections import defaultdict
from typing import Any, cast

import orjson
import yaml
from dotenv import load_dotenv

load_dotenv()

SPLIT: str = "__"

type ConfigDict = dict[str, Any]  # pyright: ignore[reportExplicitAny]


def load_from_env() -> ConfigDict:
    _config: ConfigDict = {}
    values = {k: v for k, v in os.environ.items() if k.startswith("BOTKIT__")}
    for key, value in values.items():
        parts = key[len("BOTKIT__") :].lower().split("__")
        current = _config
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                current[part] = value
            else:
                if part not in current:
                    current[part] = {}
                elif not isinstance(current[part], dict):
                    raise ValueError(f"Key {key} in environment must be a leaf")
                current = current[part]

    return load_json_recursive(_config)


def load_json_recursive(data: ConfigDict) -> ConfigDict:
    for key, value in data.items():
        if isinstance(value, dict):
            data[key] = load_json_recursive(cast("ConfigDict", value))
        elif isinstance(value, str):
            if value.lower() == "true":
                data[key] = True
            elif value.lower() == "false":
                data[key] = False
            elif value.startswith("0x"):
                with contextlib.suppress(ValueError):
                    data[key] = int(value, 16)
            else:
                with contextlib.suppress(orjson.JSONDecodeError):
                    data[key] = orjson.loads(value)
    return data


path = None
if os.path.exists("config.yaml"):
    path = "config.yaml"
elif os.path.exists("config.yml"):
    path = "config.yml"

raw_config: ConfigDict = defaultdict(dict)


def merge_dicts(dct: ConfigDict, merge_dct: ConfigDict) -> None:
    for k, v in merge_dct.items():
        if isinstance(dct.get(k), dict) and isinstance(v, dict):
            merge_dicts(cast("ConfigDict", dct[k]), cast("ConfigDict", v))
        else:
            dct[k] = v


if path:
    with open(path, encoding="utf-8") as f:
        raw_config.update(yaml.safe_load(f))

merge_dicts(raw_config, load_from_env())

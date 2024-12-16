# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import contextlib
import os
from typing import Any

import orjson
import yaml
from dotenv import load_dotenv

load_dotenv()

SPLIT: str = "__"


def load_from_env() -> dict[str, dict[str, Any]]:
    _config: dict[str, Any] = {}
    values = {k: v for k, v in os.environ.items() if k.startswith(f"BOTKIT{SPLIT}")}
    values = {k[len(f"BOTKIT{SPLIT}") :]: v for k, v in values.items()}
    current: dict[str, Any] = {}
    for key, value in values.items():
        for i, part in enumerate(key.split(SPLIT)):
            part = part.lower()  # noqa: PLW2901
            if i == 0:
                if part not in _config:
                    _config[part] = {}
                current = _config[part]
            elif i == len(key.split(SPLIT)) - 1:
                current[part] = value
            else:
                if part not in current:
                    current[part] = {}
                elif not isinstance(current[part], dict):
                    raise ValueError(f"Key {key} in environment must be a leaf")
                current = current[part]

    return load_json_recursive(_config)


def load_json_recursive(data: dict[str, Any]) -> dict[str, Any]:
    for key, value in data.items():
        if isinstance(value, dict):
            data[key] = load_json_recursive(value)
        elif isinstance(value, str):
            if value.lower() == "true":
                data[key] = True
            elif value.lower() == "false":
                data[key] = False
            else:
                with contextlib.suppress(orjson.JSONDecodeError):
                    data[key] = orjson.loads(value)
    return data


path = None
if os.path.exists("config.yaml"):
    path = "config.yaml"
elif os.path.exists("config.yml"):
    path = "config.yml"

from collections import defaultdict
def merge_dicts(dct, merge_dct):
    for k, v in merge_dct.items():
        if (isinstance(dct.get(k), dict) and isinstance(v, dict)):
            merge_dicts(dct[k], v)
        else:
            dct[k] = v

config: dict[str, dict[str, Any]] = defaultdict(dict)
if path:
    with open(path, encoding="utf-8") as f:
        config.update(yaml.safe_load(f))

merge_dicts(config, load_from_env())

# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import contextlib
import os
from collections import defaultdict
from typing import Any

import orjson
import yaml
from dotenv import load_dotenv

load_dotenv()

SPLIT: str = "__"


def load_from_env() -> dict[str, Any]:  # pyright: ignore [reportExplicitAny]
    _config: dict[str, Any] = {}  # pyright: ignore [reportExplicitAny]
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


def load_json_recursive(data: dict[str, Any]) -> dict[str, Any]:
    for key, value in data.items():
        if isinstance(value, dict):
            data[key] = load_json_recursive(value)
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

_config: dict[str, Any] = defaultdict(dict)  # pyright: ignore [reportExplicitAny]


def merge_dicts(dct: dict[str, Any], merge_dct: dict[str, Any]) -> None:  # pyright: ignore [reportExplicitAny]
    for k, v in merge_dct.items():
        if isinstance(dct.get(k), dict) and isinstance(v, dict):
            merge_dicts(dct[k], v)
        else:
            dct[k] = v


if path:
    with open(path, encoding="utf-8") as f:
        _config.update(yaml.safe_load(f))

merge_dicts(_config, load_from_env())

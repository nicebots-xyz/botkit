import yaml
import os
import orjson

from dotenv import load_dotenv
from typing import Any

load_dotenv()

SPLIT: str = "__"


def load_from_env() -> dict[str, dict[str, Any]]:

    _config = {}
    values = {k: v for k, v in os.environ.items() if k.startswith(f"BOTKIT{SPLIT}")}
    values = {k[len(f"BOTKIT{SPLIT}") :]: v for k, v in values.items()}
    current: dict = {}
    for key, value in values.items():
        for i, part in enumerate(key.split(SPLIT)):
            part = part.lower()
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
                try:
                    data[key] = orjson.loads(value)
                except orjson.JSONDecodeError:
                    pass
    return data


path = None
if os.path.exists("config.yaml"):
    path = "config.yaml"
elif os.path.exists("config.yml"):
    path = "config.yml"


if path:
    # noinspection PyArgumentEqualDefault
    with open(path, "r", encoding="utf-8") as f:
        config: dict[str, dict[str, Any]] = yaml.safe_load(f)
else:
    config: dict[str, dict[str, Any]] = load_from_env()

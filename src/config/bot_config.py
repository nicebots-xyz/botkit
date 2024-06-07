import yaml
import os

from typing import Any

if os.path.exists("config.yaml"):
    path = "config.yaml"
elif os.path.exists("config.yml"):
    path = "config.yml"
else:
    raise FileNotFoundError("Configuration file not found")

with open(path, "r", encoding="utf-8") as f:
    config: dict[str, dict[str, Any]] = yaml.safe_load(f)

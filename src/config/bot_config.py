import yaml
from typing import Any

with open('config.yaml', 'r', encoding='utf-8') as f:
    config: dict[str, dict[str, Any]] = yaml.safe_load(f)

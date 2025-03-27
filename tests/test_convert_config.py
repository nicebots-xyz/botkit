# Copyright (c) NiceBots
# SPDX-License-Identifier: MIT

import os
import tempfile
from pathlib import Path

from scripts.convert_config.convert import env_to_yaml, yaml_to_env


def test_yaml_to_env() -> None:
    yaml_content = """
    bot:
      token: "your_bot_token"
    extensions:
      listings:
        enabled: false
        topgg_token: "your_top.gg_token"
      ping:
        enabled: true
    logging:
      level: INFO
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as yaml_file:
        yaml_file.write(yaml_content.encode("utf-8"))
        yaml_path = Path(yaml_file.name)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".env") as env_file:
        env_path = Path(env_file.name)

    yaml_to_env(yaml_path, env_path)

    with env_path.open("r", encoding="utf-8") as env_file:
        env_content = env_file.read()

    expected_env_content = (
        "BOTKIT__bot__token=your_bot_token\n"
        "BOTKIT__extensions__listings__enabled=false\n"
        "BOTKIT__extensions__listings__topgg_token=your_top.gg_token\n"
        "BOTKIT__extensions__ping__enabled=true\n"
        "BOTKIT__logging__level=INFO\n"
    )

    assert env_content == expected_env_content

    os.remove(yaml_path)
    os.remove(env_path)


def test_env_to_yaml() -> None:
    env_content = (
        "BOTKIT__bot__token=your_bot_token\n"
        "BOTKIT__extensions__listings__enabled=false\n"
        "BOTKIT__extensions__listings__topgg_token=your_top.gg_token\n"
        "BOTKIT__extensions__ping__enabled=true\n"
        "BOTKIT__logging__level=INFO\n"
        "SOME_OTHER_VAR=should_be_ignored\n"  # This should be ignored
    )
    with tempfile.NamedTemporaryFile(delete=False, suffix=".env") as env_file:
        env_file.write(env_content.encode("utf-8"))
        env_path = Path(env_file.name)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as yaml_file:
        yaml_path = Path(yaml_file.name)

    env_to_yaml(env_path, yaml_path)

    with yaml_path.open("r", encoding="utf-8") as yaml_file:
        yaml_content = yaml_file.read()

    expected_yaml_content = (
        "bot:\n"
        "  token: your_bot_token\n"
        "extensions:\n"
        "  listings:\n"
        "    enabled: false\n"
        "    topgg_token: your_top.gg_token\n"
        "  ping:\n"
        "    enabled: true\n"
        "logging:\n"
        "  level: INFO\n"
    )

    assert yaml_content == expected_yaml_content

    os.remove(env_path)
    os.remove(yaml_path)

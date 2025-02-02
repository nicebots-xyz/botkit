# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

# ruff: noqa: S101, S105

import os
from typing import Any

import yaml

from src.config.bot_config import load_from_env, merge_dicts


def test_merge_dicts_basic() -> None:
    """Test basic dictionary merging."""
    base = {"a": 1, "b": 2}
    update = {"b": 3, "c": 4}
    merge_dicts(base, update)
    assert base == {"a": 1, "b": 3, "c": 4}


def test_merge_dicts_nested() -> None:
    """Test nested dictionary merging."""
    base = {"a": {"x": 1, "y": 2}, "b": 3}
    update = {"a": {"y": 4, "z": 5}, "c": 6}
    merge_dicts(base, update)
    assert base == {"a": {"x": 1, "y": 4, "z": 5}, "b": 3, "c": 6}


def test_merge_dicts_deep_nested() -> None:
    """Test deeply nested dictionary merging."""
    base = {"a": {"x": {"p": 1, "q": 2}, "y": 3}}
    update = {"a": {"x": {"q": 4, "r": 5}}}
    merge_dicts(base, update)
    assert base == {"a": {"x": {"p": 1, "q": 4, "r": 5}, "y": 3}}


def test_merge_dicts_with_none() -> None:
    """Test merging when values are None."""
    base = {"a": {"x": 1}, "b": None}
    update = {"a": {"y": 2}, "b": {"z": 3}}
    merge_dicts(base, update)
    assert base == {"a": {"x": 1, "y": 2}, "b": {"z": 3}}


def test_load_from_env() -> None:
    """Test loading configuration from environment variables."""
    # Set up test environment variables
    test_env = {
        "BOTKIT__TOKEN": "test-token",
        "BOTKIT__EXTENSIONS__PING__ENABLED": "true",
        "BOTKIT__EXTENSIONS__PING__COLOR": "0xFF0000",
        "BOTKIT__EXTENSIONS__TOPGG__TOKEN": "test-topgg-token",
    }

    for key, value in test_env.items():
        os.environ[key] = value

    try:
        config = load_from_env()

        # Check the loaded configuration
        assert config["token"] == "test-token"
        assert config["extensions"]["ping"]["enabled"] is True
        assert config["extensions"]["ping"]["color"] == 0xFF0000
        assert config["extensions"]["topgg"]["token"] == "test-topgg-token"

    finally:
        # Clean up environment variables
        for key in test_env:
            os.environ.pop(key, None)


def test_config_file_and_env_integration(tmp_path: Any) -> None:
    """Test integration of config file and environment variables."""
    # Create a temporary config file
    config_file = tmp_path / "config.yaml"
    config_data = {
        "token": "file-token",
        "extensions": {"ping": {"enabled": False, "color": 0x00FF00, "message": "Pong!"}, "topgg": {"enabled": True}},
    }

    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)

    # Set environment variables that should override some values
    test_env = {
        "BOTKIT__TOKEN": "env-token",
        "BOTKIT__EXTENSIONS__PING__ENABLED": "true",
        "BOTKIT__EXTENSIONS__PING__COLOR": "0xFF0000",
    }

    for key, value in test_env.items():
        os.environ[key] = value

    try:
        # Load config from file
        with open(config_file, encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # Merge with environment variables
        env_config = load_from_env()
        merge_dicts(config, env_config)

        # Verify the merged configuration
        assert config["token"] == "env-token"  # Overridden by env
        assert config["extensions"]["ping"]["enabled"] is True  # Overridden by env
        assert config["extensions"]["ping"]["color"] == 0xFF0000  # Overridden by env
        assert config["extensions"]["ping"]["message"] == "Pong!"  # Kept from file
        assert config["extensions"]["topgg"]["enabled"] is True  # Kept from file

    finally:
        # Clean up environment variables
        for key in test_env:
            os.environ.pop(key, None)

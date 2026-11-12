# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

# ruff: noqa: S106

import pytest
from tortoise_extensions.s3 import S3Storage

from src.config.models import DbConfig, DbExtraApp, S3StorageConfig
from src.database.config import get_s3_storages


def _s3(endpoint: str, *, ssl: bool = True) -> S3StorageConfig:
    return S3StorageConfig(endpoint=endpoint, bucket="bucket", access_key="key", secret_key="secret", ssl=ssl)


def test_no_s3_config() -> None:
    """Test that nothing is registered without S3 configuration."""
    db = DbConfig(url="", extra_apps={"analytics": DbExtraApp()})
    assert get_s3_storages(db) == {}


def test_main_app_and_fallback() -> None:
    """Test that extra apps without `s3` inherit the top-level storage."""
    db = DbConfig(url="", s3=_s3("s3.example.com"), extra_apps={"analytics": DbExtraApp()})
    storages = get_s3_storages(db)
    assert storages.keys() == {"models", "analytics"}
    assert storages["analytics"] == storages["models"]
    assert storages["models"] == S3Storage(
        endpoint="s3.example.com", bucket="bucket", access_key="key", secret_key="secret"
    )


def test_per_app_override_and_ssl() -> None:
    """Test that an extra app can use its own storage with SSL disabled."""
    db = DbConfig(
        url="",
        s3=_s3("s3.example.com"),
        extra_apps={"local": DbExtraApp(s3=_s3("minio:9000", ssl=False))},
    )
    storages = get_s3_storages(db)
    assert storages["models"].ssl
    assert storages["local"].endpoint == "minio:9000"
    assert not storages["local"].ssl


def test_named_storages() -> None:
    """Test that named storages are registered without a main storage."""
    db = DbConfig(url="", s3_storages={"cdn": _s3("cdn.example.com")})
    assert get_s3_storages(db).keys() == {"cdn"}


def test_named_storage_clash() -> None:
    """Test that named storages cannot reuse Tortoise app names."""
    db = DbConfig(url="", s3_storages={"models": _s3("cdn.example.com")})
    with pytest.raises(ValueError, match="models"):
        get_s3_storages(db)

# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

# ruff: noqa: S106

import pytest
from pydantic import ValidationError
from tortoise_extensions.s3 import LocalStorage, MemoryStorage, S3Storage

from src.config.models import DbConfig, DbExtraApp, LocalStorageConfig, MemoryStorageConfig, S3StorageConfig
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
    assert storages["models"] == S3Storage(
        endpoint="s3.example.com", bucket="bucket", access_key="key", secret_key="secret", ssl=True
    )
    assert storages["local"] == S3Storage(
        endpoint="minio:9000", bucket="bucket", access_key="key", secret_key="secret", ssl=False
    )


def test_named_storages() -> None:
    """Test that named storages are registered without a main storage."""
    db = DbConfig(url="", s3_storages={"cdn": _s3("cdn.example.com")})
    assert get_s3_storages(db).keys() == {"cdn"}


def test_named_storage_clash() -> None:
    """Test that named storages cannot reuse Tortoise app names."""
    db = DbConfig(url="", s3_storages={"models": _s3("cdn.example.com")})
    with pytest.raises(ValueError, match="models"):
        get_s3_storages(db)


def test_memory_and_local_storages() -> None:
    """Test that memory and local configurations map to their storages."""
    db = DbConfig(
        url="",
        s3=MemoryStorageConfig(type="memory"),
        s3_storages={"files": LocalStorageConfig(type="local", path="objects")},
    )
    storages = get_s3_storages(db)
    assert storages["models"] == MemoryStorage()
    assert storages["files"] == LocalStorage(path="objects")


def test_type_defaults_to_s3() -> None:
    """Test that a storage without `type` is parsed as S3."""
    db = DbConfig.model_validate(
        {"url": "", "s3": {"endpoint": "s3.example.com", "bucket": "b", "access_key": "k", "secret_key": "s"}}
    )
    assert isinstance(db.s3, S3StorageConfig)


def test_type_override_ignores_s3_keys() -> None:
    """Test that overriding `type` (e.g. `BOTKIT__DB__S3__TYPE=memory`) ignores leftover S3 keys."""
    db = DbConfig.model_validate({"url": "", "s3": {"type": "memory", "endpoint": "s3.example.com", "bucket": "b"}})
    assert get_s3_storages(db) == {"models": MemoryStorage()}


def test_unknown_type() -> None:
    """Test that an unknown storage type is rejected."""
    with pytest.raises(ValidationError):
        DbConfig.model_validate({"url": "", "s3": {"type": "ftp"}})

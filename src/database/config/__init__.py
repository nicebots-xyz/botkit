# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz


import ssl
from collections import defaultdict
from logging import getLogger
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import aerich
from tortoise import Tortoise

from src.config import config

logger = getLogger("bot").getChild("database")


def create_ssl_context() -> ssl.SSLContext:
    """Create SSL context for Database connection."""
    cert_paths = [
        Path(__file__).parent.parent.parent / ".postgres" / "root.crt",
        Path.cwd() / ".postgres" / "root.crt",
    ]

    cert_path = None
    for path in cert_paths:
        if path.exists():
            cert_path = path
            break

    if cert_path is None:
        logger.error("Database certificate not found!")
        raise FileNotFoundError("Database SSL certificate not found")

    logger.debug(f"Loading SSL certificate from: {cert_path}")

    with open(cert_path) as f:
        cert_content = f.read()
        logger.debug(f"Certificate loaded, length: {len(cert_content)} bytes")

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED

    ssl_context.load_verify_locations(cafile=str(cert_path))

    logger.debug(
        f"SSL context created: verify_mode={ssl_context.verify_mode}, check_hostname={ssl_context.check_hostname}"
    )
    logger.debug("SSL context will ONLY trust the custom CA cert (no system CAs)")

    return ssl_context


def parse_postgres_url(url: str) -> dict[str, Any]:
    """Parse postgres URL into credentials dict.

    Returns a dictionary that can contain various types for asyncpg connection.
    Query parameters are added as-is (single values unwrapped from lists).
    """
    parsed = urlparse(url)

    query_params = parse_qs(parsed.query)

    credentials: dict[str, Any] = {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "user": parsed.username,
        "password": parsed.password,
        "database": parsed.path.lstrip("/"),
    }

    for key, value in query_params.items():
        if key not in ["ssl", "sslmode"]:  # Skip SSL params
            # Unwrap single-item lists for cleaner values
            credentials[key] = value[0] if len(value) == 1 else value

    return credentials


def apply_params(uri: str, params: dict[str, Any] | None) -> str:
    if params is None:
        return uri

    first: bool = True
    for param, value in params.items():
        if param == "ssl":
            continue
        if value is not None:
            uri += f"{'?' if first else '&'}{param}={value}"
            first = False
    return uri


def get_app_url_mapping() -> dict[str, str]:
    return {
        app_name: apply_params(app_config.url or config.db.url, app_config.params)
        for app_name, app_config in config.db.extra_apps.items()
    }


def get_url_apps_mapping() -> dict[str, list[str]]:
    app_url_mapping: dict[str, str] = get_app_url_mapping()
    mapping: dict[str, list[str]] = defaultdict(list)

    for app_name, app_url in app_url_mapping.items():
        mapping[app_url].append(app_name)

    return mapping


def parse_url_apps_mapping(url_apps_mapping: dict[str, list[str]]) -> tuple[dict[str, str], dict[str, dict[str, Any]]]:
    app_connection: dict[str, str] = {}
    connection_config: dict[str, dict[str, Any]] = {}

    ssl_context = create_ssl_context() if config.db.params and config.db.params.get("ssl") else None

    for i, (url, apps) in enumerate(url_apps_mapping.items()):
        connection_name = f"connection_{i}"

        credentials = parse_postgres_url(url)
        if ssl_context:
            credentials["ssl"] = ssl_context

        logger.debug(f"Connection {connection_name} credentials keys: {list(credentials.keys())}")
        logger.debug(f"SSL in credentials: {'ssl' in credentials}")

        connection_config[connection_name] = {"engine": "tortoise.backends.asyncpg", "credentials": credentials}

        for app in apps:
            app_connection[app] = connection_name

    app_connection["models"] = "default"
    default_url = apply_params(config.db.url, config.db.params)

    logger.debug(f"Default URL (sanitized): {default_url.split('@')[1] if '@' in default_url else 'N/A'}")

    credentials = parse_postgres_url(default_url)
    if ssl_context:
        credentials["ssl"] = ssl_context

    logger.debug(f"Default connection credentials keys: {list(credentials.keys())}")
    logger.debug(f"SSL in credentials: {'ssl' in credentials}")
    if "ssl" in credentials:
        logger.debug(f"SSL value type: {type(credentials['ssl'])}")

    connection_config["default"] = {"engine": "tortoise.backends.asyncpg", "credentials": credentials}

    return app_connection, connection_config


_app_conn_map: dict[str, str]
_conn_cfg_map: dict[str, dict[str, Any]]

_app_conn_map, _conn_cfg_map = parse_url_apps_mapping(get_url_apps_mapping())

APP_CONNECTION_MAPPING: dict[str, str] = _app_conn_map
CONNECTION_CONFIG_MAPPING: dict[str, dict[str, Any]] = _conn_cfg_map


def get_apps() -> dict[str, dict[str, list[str] | str]]:
    apps = {
        app_name: {
            "models": app.models,
            "default_connection": APP_CONNECTION_MAPPING[app_name],
        }
        for app_name, app in config.db.extra_apps.items()
    }
    apps["models"] = {
        "models": ["src.database.models", "aerich.models"],
        "default_connection": "default",
    }
    return apps


TORTOISE_ORM = {
    "connections": CONNECTION_CONFIG_MAPPING,
    "apps": get_apps(),
}


async def init() -> None:
    command = aerich.Command(
        TORTOISE_ORM,
        app="models",
        location="./src/database/migrations/",
    )
    await command.init()
    migrated = await command.upgrade(run_in_transaction=True)
    logger.success(f"Successfully migrated {migrated} migrations")  # pyright: ignore[reportAttributeAccessIssue]
    await Tortoise.init(config=TORTOISE_ORM)


async def shutdown() -> None:
    await Tortoise.close_connections()


__all__ = ["APP_CONNECTION_MAPPING", "init", "shutdown"]

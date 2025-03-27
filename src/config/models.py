# Copyright (c) NiceBots
# SPDX-License-Identifier: MIT

from typing import Any, Literal, overload, override

from pydantic import BaseModel

type Extension = dict[str, Any]


class RedisConfig(BaseModel):
    host: str
    port: int
    password: str | None = None
    db: int
    ssl: bool


class CacheConfig(BaseModel):
    type: Literal["memory", "redis"] = "memory"
    redis: RedisConfig | None = None


class PrefixConfig(BaseModel):
    prefix: str
    enabled: bool = True

    def __bool__(self) -> bool:
        return self.enabled

    @override
    def __str__(self) -> str:
        return self.prefix if self.enabled else ""


class SlashConfig(BaseModel):
    enabled: bool = True

    def __bool__(self) -> bool:
        return self.enabled


class RestConfig(BaseModel):
    enabled: bool = False
    health: bool = False
    host: str = "0.0.0.0"  # noqa: S104
    port: int = 6000

    def __bool__(self) -> bool:
        return self.enabled


class BotConfig(BaseModel):
    token: str
    public_key: str | None = None
    prefix: PrefixConfig | str = PrefixConfig(prefix="!", enabled=False)
    slash: SlashConfig = SlashConfig(enabled=False)
    cache: CacheConfig = CacheConfig()
    rest: RestConfig = RestConfig()


class LoggingConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "SUCCESS", "ERROR", "CRITICAL"] = "INFO"


class UseConfig(BaseModel):
    bot: bool = True
    backend: bool = False


class DbConfig(BaseModel):
    url: str
    enabled: bool = True


class Config(BaseModel):
    db: DbConfig = DbConfig(url="", enabled=False)
    bot: BotConfig = BotConfig(token="")
    logging: LoggingConfig = LoggingConfig()
    use: UseConfig = UseConfig()
    extensions: dict[str, Extension] = {}

    @overload
    def get_extension(self, name: str, default: None) -> tuple[str, Extension]: ...

    @overload
    def get_extension[T](self, name: str, default: T) -> tuple[str, Extension | T]: ...

    def get_extension[T](self, name: str, default: T | None = None) -> tuple[str, Extension | T]:
        if name in self.extensions:
            return name, self.extensions[name]
        if (name := name.replace("_", "-")) in self.extensions:
            return name, self.extensions[name]
        if default is not None:
            return name, default
        raise KeyError(f"Extension {name} not found in config")

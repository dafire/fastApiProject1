import os
from functools import lru_cache
from typing import TypeVar
from urllib.parse import quote_plus

import dotenv
from loguru import logger
from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["Settings", "DatabaseSettings", "get_settings"]

TSettings = TypeVar("TSettings", bound=BaseSettings)


@lru_cache()
def get_settings(cls: type[TSettings]) -> TSettings:
    res = dotenv.load_dotenv(".env")
    if res:
        logger.debug("Loaded .env file for '{}'", cls.__name__)
    return cls()


class Settings(BaseSettings):
    secret_key: str = Field()
    debug: bool = Field(default=False)

    static_folder: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
    template_folder: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))

    redis_url: AnyUrl = Field(default="redis://localhost:6379/0")


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="database_")

    driver: str = "postgresql+asyncpg"
    name: str = "postgres"
    username: str = "postgres"
    password: str = "x"
    host: str = "localhost"
    port: int = 5434

    echo: bool = False

    @property
    def url(self) -> str:
        password = quote_plus(self.password)
        return f"{self.driver}://{self.username}:{password}@{self.host}:{self.port}/{self.name}"

    @property
    def sync_url(self) -> str:
        password = quote_plus(self.password)
        if "+asyncpg" in self.driver:
            sync_driver = self.driver.replace("+asyncpg", "")
        else:
            sync_driver = self.driver
        return f"{sync_driver}://{self.username}:{password}@{self.host}:{self.port}/{self.name}"


class AuthSettings(BaseSettings):
    google_client_id: str | None
    google_client_secret: str | None
    discord_client_id: str | int | None
    discord_client_secret: str | None

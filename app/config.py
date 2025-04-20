# Модель лоя получения настроек из .env

from typing import Optional, Union

from pydantic import Field, SecretStr, EmailStr
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

class Project(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="project_")

    name: Optional[str] = ""
    version: Optional[str] = ""
    info: Optional[str] = ""
    root: str


class Author(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="author_")

    tg_id: Optional[int] = None
    tg_username: Optional[str] = ""
    email: Optional[Union[EmailStr, str]] = ""


class BotConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="tg_")
    token: SecretStr
    users: str

    @computed_field
    def user_ids(self) -> list:

        if not self.users:
            return []

        _list = self.users.split(",")
        if _list:
            return list(map(int, _list))
        return []


class Config(BaseSettings):
    model_config = SettingsConfigDict()

    project: Project = Field(default_factory=Project)
    author: Author = Field(default_factory=Author)
    bot: BotConfig = Field(default_factory=BotConfig)

    @classmethod
    def load(cls) -> "Config":
        return cls()


CONFIG = Config()

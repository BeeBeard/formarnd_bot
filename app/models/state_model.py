# Модель лоя получения настроек из .env

from typing import Optional, Union

from pydantic import Field, SecretStr, EmailStr
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    pass





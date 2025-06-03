from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"

    db_url: str = ""

    jwt_secret_key: str = ""
    jwt_expiration_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env")

    allowed_origins: list[str] = ["http://localhost"]


@lru_cache
def get_settings():
    return Settings()

from functools import lru_cache 
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Address API"
    app_version: str = "1.0.0"
    database_url: str = "sqlite:///./address_api.db"
    log_level: str = "INFO"

@lru_cache
def get_settings():
    return Settings()
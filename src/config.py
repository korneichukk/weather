from pathlib import Path
from functools import lru_cache
from pydantic import computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_ROOT: Path = Path(__file__).parent.parent.resolve()
    PROJECT_NAME: str = "Weather API"
    WEATHER_DATA_DIR: Path = PROJECT_ROOT / "weather_data"

    OPEN_WEATHER_API_KEY: str = ""
    WEATHERAPI_API_KEY: str = ""
    SQLITE_DB_NAME: str = "db.sqlite3"

    REDIS_BROKER: str = "redis://localhost:6379/0"
    REDIS_BACKEND: str = "redis://localhost:6379/0"

    @field_validator("REDIS_BROKER", "REDIS_BACKEND")
    def validate_redis_url(cls, v: str):
        if not v.startswith("redis://"):
            raise ValueError("Invalid Redis URL, must start with redis://")

        return v

    @computed_field
    @property
    def ASYNC_SQLITE_ALCHEMY_URI(self) -> str:
        schema = "sqlite+aiosqlite"
        return f"{schema}:///{self.PROJECT_ROOT}/{self.SQLITE_DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env", env_ignore_empty=True, extra="ignore"
    )


@lru_cache
def get_settings():
    return Settings()

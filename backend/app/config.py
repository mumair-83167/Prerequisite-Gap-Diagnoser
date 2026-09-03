from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: Optional[str] = None
    PORT: int = 8000
    HOST: str = "127.0.0.1"
    ENVIRONMENT: str = "development"
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    MOCK_LLM: bool = True
    SQLITE_DB_PATH: str = "app/db/session_store.sqlite"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

"""Configuration management for Nocturna Telegram Bot."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Telegram Bot Configuration
    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    telegram_bot_username: Optional[str] = Field(None, alias="TELEGRAM_BOT_USERNAME")

    # Nocturna API Configuration
    nocturna_api_url: str = Field(
        default="http://localhost:8000/api", alias="NOCTURNA_API_URL"
    )
    nocturna_service_token: Optional[str] = Field(None, alias="NOCTURNA_SERVICE_TOKEN")
    nocturna_timeout: int = Field(default=30, alias="NOCTURNA_TIMEOUT")
    nocturna_max_retries: int = Field(default=3, alias="NOCTURNA_MAX_RETRIES")

    # OpenRouter Configuration
    openrouter_api_key: Optional[str] = Field(None, alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(
        default="anthropic/claude-haiku-4.5", alias="OPENROUTER_MODEL"
    )

    # Application Settings
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    timezone: str = Field(default="Europe/Moscow", alias="TIMEZONE")

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def validate(self) -> None:
        """Validate configuration settings."""
        if not self.nocturna_api_url.startswith(("http://", "https://")):
            raise ValueError("Invalid NOCTURNA_API_URL format")

        if self.nocturna_timeout <= 0:
            raise ValueError("NOCTURNA_TIMEOUT must be positive")

        if self.nocturna_max_retries < 0:
            raise ValueError("NOCTURNA_MAX_RETRIES must be non-negative")


def get_settings() -> Settings:
    """Get application settings instance."""
    settings = Settings()
    settings.validate()
    return settings


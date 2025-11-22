"""Configuration management for Nocturna Telegram Bot."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


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

    # Chart Service Configuration
    chart_service_url: str = Field(
        alias="CHART_SERVICE_URL"
    )
    chart_service_api_key: str = Field(alias="NOCTURNA_IMAGE_SERVICE_TOKEN")
    chart_service_timeout: int = Field(default=60, alias="CHART_SERVICE_TIMEOUT")

    # Application Settings
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    timezone: str = Field(default="Europe/Moscow", alias="TIMEZONE")

    # Bot Mode Configuration
    bot_mode: str = Field(default="polling", alias="BOT_MODE")  # polling or webhook
    webhook_url: Optional[str] = Field(None, alias="WEBHOOK_URL")
    webhook_path: str = Field(default="/webhook", alias="WEBHOOK_PATH")
    webhook_port: int = Field(default=8080, alias="WEBHOOK_PORT")
    webhook_host: str = Field(default="0.0.0.0", alias="WEBHOOK_HOST")
    webhook_secret: Optional[str] = Field(None, alias="WEBHOOK_SECRET")

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from environment
    )

    def validate(self) -> None:
        """Validate configuration settings."""
        if not self.nocturna_api_url.startswith(("http://", "https://")):
            raise ValueError("Invalid NOCTURNA_API_URL format")

        if self.nocturna_timeout <= 0:
            raise ValueError("NOCTURNA_TIMEOUT must be positive")

        if self.nocturna_max_retries < 0:
            raise ValueError("NOCTURNA_MAX_RETRIES must be non-negative")

        # Validate bot mode
        if self.bot_mode not in ["polling", "webhook"]:
            raise ValueError("BOT_MODE must be 'polling' or 'webhook'")

        # Validate webhook configuration if in webhook mode
        if self.bot_mode == "webhook":
            if not self.webhook_url:
                raise ValueError("WEBHOOK_URL is required in webhook mode")
            if not self.webhook_url.startswith("https://"):
                raise ValueError("WEBHOOK_URL must use HTTPS")
            if self.webhook_port <= 0 or self.webhook_port > 65535:
                raise ValueError("WEBHOOK_PORT must be between 1 and 65535")


def get_settings() -> Settings:
    """Get application settings instance."""
    settings = Settings()
    settings.validate()
    return settings


"""
Application configuration using Pydantic Settings.

All settings can be overridden via environment variables
with the KLYDO_ prefix.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    Loaded from environment variables or .env file.
    All env vars should be prefixed with KLYDO_.

    Example:
        KLYDO_DEBUG=true
        KLYDO_DEFAULT_SCRAPER=myntra
    """

    model_config = SettingsConfigDict(
        env_prefix="KLYDO_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Scraper settings
    default_scraper: str = "myntra"
    request_timeout: int = 30
    cache_ttl: int = 3600  # 1 hour

    # Rate limiting (be nice to servers)
    requests_per_minute: int = 30

    # Klydo brand API auth
    klydo_api_token: str | None = None
    klydo_session_id: str | None = None

    # Debug mode
    debug: bool = False


# Singleton instance
settings = Settings()

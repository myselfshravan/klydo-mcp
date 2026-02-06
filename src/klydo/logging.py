"""
Logging configuration using Loguru.

Provides structured, human-readable logging for the Klydo MCP server.
Logs are essential for tracking requests, debugging issues, and monitoring
the server in production.

Usage:
    from klydo.logging import logger

    logger.info("Search request", query="black dress", limit=10)
    logger.debug("Cache hit", key="search:dress")
    logger.error("API error", exc_info=True)
"""

import sys
from typing import Any

from loguru import logger

from klydo.config import settings

# Remove default handler
logger.remove()

# Configure log format based on debug mode
if settings.debug:
    # Detailed format for development
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    log_level = "DEBUG"
else:
    # Cleaner format for production
    log_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} | {message}"
    )
    log_level = "INFO"

# Add stdout handler
logger.add(
    sys.stderr,
    format=log_format,
    level=log_level,
    colorize=True,
    backtrace=settings.debug,
    diagnose=settings.debug,
)


def log_request(
    action: str,
    **kwargs: Any,
) -> None:
    """
    Log an incoming MCP tool request.

    Args:
        action: The action being performed (e.g., "search", "get_product")
        **kwargs: Additional context to log
    """
    logger.info(f"Request: {action}", **kwargs)


def log_response(
    action: str,
    duration_ms: float,
    result_count: int | None = None,
    **kwargs: Any,
) -> None:
    """
    Log a completed MCP tool response.

    Args:
        action: The action that was performed
        duration_ms: Time taken in milliseconds
        result_count: Number of results returned (if applicable)
        **kwargs: Additional context to log
    """
    msg = f"Response: {action} completed in {duration_ms:.0f}ms"
    if result_count is not None:
        msg += f" ({result_count} results)"
    logger.info(msg, **kwargs)


def log_cache_hit(key: str) -> None:
    """Log a cache hit."""
    logger.debug(f"Cache HIT: {key}")


def log_cache_miss(key: str) -> None:
    """Log a cache miss."""
    logger.debug(f"Cache MISS: {key}")


def log_api_call(
    source: str,
    endpoint: str,
    method: str = "GET",
) -> None:
    """Log an outgoing API call."""
    logger.debug(f"API call: {method} {source} {endpoint}")


def log_api_error(
    source: str,
    endpoint: str,
    error: str,
    status_code: int | None = None,
) -> None:
    """Log an API error."""
    msg = f"API error: {source} {endpoint}"
    if status_code:
        msg += f" (HTTP {status_code})"
    msg += f" - {error}"
    logger.warning(msg)


def log_scraper_error(
    scraper: str,
    operation: str,
    error: Exception,
) -> None:
    """Log a scraper error with exception details."""
    logger.error(f"Scraper error: {scraper}.{operation} - {error}")


# Export logger and helper functions
__all__ = [
    "logger",
    "log_request",
    "log_response",
    "log_cache_hit",
    "log_cache_miss",
    "log_api_call",
    "log_api_error",
    "log_scraper_error",
]

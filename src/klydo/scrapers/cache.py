"""
Simple file-based cache with TTL support.

This provides caching for scraper responses to:
- Reduce load on target sites
- Improve response times
- Work offline with cached data

Can be swapped for Redis or other backends later.
"""

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class CacheEntry(BaseModel):
    """
    Cache entry with data and expiration.

    Attributes:
        data: Cached data (dict or list)
        expires_at: When this entry expires (UTC)
    """

    data: dict[str, Any] | list[Any]
    expires_at: datetime


class Cache:
    """
    File-based cache with TTL support.

    Each cache entry is stored as a JSON file with expiration metadata.
    Expired entries are cleaned up on read.

    Usage:
        cache = Cache(namespace="myntra")

        # Try cache first
        if cached := await cache.get("search:dress"):
            return cached

        # Fetch and cache
        result = await fetch_data()
        await cache.set("search:dress", result, ttl=3600)

    Attributes:
        namespace: Cache namespace (used in key hashing)
        cache_dir: Directory for cache files
        default_ttl: Default TTL in seconds
    """

    def __init__(
        self,
        namespace: str,
        cache_dir: Path | None = None,
        default_ttl: int = 3600,
    ):
        """
        Initialize cache.

        Args:
            namespace: Cache namespace (e.g., 'myntra')
            cache_dir: Directory for cache files (default: ~/.cache/klydo)
            default_ttl: Default TTL in seconds (default: 1 hour)
        """
        self.namespace = namespace
        self.cache_dir = cache_dir or Path.home() / ".cache" / "klydo"
        self.default_ttl = default_ttl

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key_to_path(self, key: str) -> Path:
        """
        Convert cache key to file path.

        Uses MD5 hash to create safe filenames.

        Args:
            key: Cache key

        Returns:
            Path to cache file
        """
        full_key = f"{self.namespace}:{key}"
        hashed = hashlib.md5(full_key.encode()).hexdigest()
        return self.cache_dir / f"{hashed}.json"

    async def get(self, key: str) -> dict[str, Any] | list[Any] | None:
        """
        Get cached value if exists and not expired.

        Args:
            key: Cache key

        Returns:
            Cached data, or None if not found/expired
        """
        path = self._key_to_path(key)

        if not path.exists():
            return None

        try:
            raw = path.read_text(encoding="utf-8")
            entry = CacheEntry.model_validate_json(raw)

            # Check expiration
            now = datetime.now(timezone.utc)
            if entry.expires_at < now:
                # Expired, clean up
                path.unlink(missing_ok=True)
                return None

            return entry.data

        except (json.JSONDecodeError, ValueError):
            # Corrupted cache file, remove it
            path.unlink(missing_ok=True)
            return None

    async def set(
        self,
        key: str,
        value: dict[str, Any] | list[Any],
        ttl: int | None = None,
    ) -> None:
        """
        Cache a value with TTL.

        Args:
            key: Cache key
            value: Data to cache (must be JSON-serializable)
            ttl: TTL in seconds (default: use default_ttl)
        """
        ttl = ttl or self.default_ttl
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)

        entry = CacheEntry(data=value, expires_at=expires_at)

        path = self._key_to_path(key)
        path.write_text(entry.model_dump_json(), encoding="utf-8")

    async def invalidate(self, key: str) -> bool:
        """
        Remove a cached value.

        Args:
            key: Cache key

        Returns:
            True if entry was removed, False if not found
        """
        path = self._key_to_path(key)

        if path.exists():
            path.unlink()
            return True

        return False

    async def clear(self) -> int:
        """
        Clear all cached entries for this namespace.

        Note: This clears ALL entries in the cache directory,
        not just this namespace. Use with caution.

        Returns:
            Number of entries cleared
        """
        count = 0
        for path in self.cache_dir.glob("*.json"):
            path.unlink()
            count += 1
        return count

    def cache_key(self, *parts: str) -> str:
        """
        Build a cache key from parts.

        Args:
            *parts: Key parts to join

        Returns:
            Cache key string

        Example:
            key = cache.cache_key("search", "dress", "women")
            # Returns: "search:dress:women"
        """
        return ":".join(str(p) for p in parts if p)

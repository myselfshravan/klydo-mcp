"""
Scraper layer for fashion e-commerce sites.

This module provides a unified interface for scraping
fashion products from various Indian e-commerce sites.

Usage:
    from klydo.scrapers import get_scraper

    scraper = get_scraper("myntra")
    products = await scraper.search("black dress")
"""

from klydo.scrapers.base import ScraperProtocol

# Registry of available scrapers
# Import here to avoid circular imports
_SCRAPERS: dict[str, type[ScraperProtocol]] = {}


def _register_scrapers() -> None:
    """Lazy registration of scrapers to avoid circular imports."""
    global _SCRAPERS
    if not _SCRAPERS:
        from klydo.scrapers.myntra import MyntraScraper
        from klydo.scrapers.klydo_store import KlydoStoreScraper

        _SCRAPERS["myntra"] = MyntraScraper
        _SCRAPERS["klydo"] = KlydoStoreScraper


def get_scraper(name: str = "myntra") -> ScraperProtocol:
    """
    Factory function to get a scraper instance by name.

    Args:
        name: Scraper name (e.g., 'myntra', 'ajio')

    Returns:
        Scraper instance implementing ScraperProtocol

    Raises:
        ValueError: If scraper name is not registered

    Example:
        scraper = get_scraper("myntra")
        products = await scraper.search("dress")
    """
    _register_scrapers()

    if name not in _SCRAPERS:
        available = list(_SCRAPERS.keys())
        raise ValueError(
            f"Unknown scraper: '{name}'. Available scrapers: {available}"
        )

    return _SCRAPERS[name]()


def list_scrapers() -> list[str]:
    """
    List all available scraper names.

    Returns:
        List of registered scraper names
    """
    _register_scrapers()
    return list(_SCRAPERS.keys())


__all__ = [
    "ScraperProtocol",
    "get_scraper",
    "list_scrapers",
]

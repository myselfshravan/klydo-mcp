"""
Abstract scraper interface using Python Protocol.

This defines the contract that all scrapers must implement.
Using Protocol (structural subtyping) instead of ABC for:
- Duck typing with type safety
- No inheritance required
- Easy to mock in tests
- Clear interface for AI agents to understand
"""

from typing import Protocol, runtime_checkable

from klydo.models.product import Product, ProductSummary


@runtime_checkable
class ScraperProtocol(Protocol):
    """
    Abstract scraper interface.

    Implement this protocol for any fashion e-commerce site.
    All methods are async to support non-blocking I/O.

    Example implementation:
        class MyScraper:
            @property
            def source_name(self) -> str:
                return "mysite"

            async def search(self, query: str, **kwargs) -> list[ProductSummary]:
                # Implementation here
                ...
    """

    @property
    def source_name(self) -> str:
        """
        Human-readable source name.

        Returns:
            Source name (e.g., 'Myntra', 'Ajio')
        """
        ...

    async def search(
        self,
        query: str,
        *,
        category: str | None = None,
        gender: str | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        limit: int = 20,
    ) -> list[ProductSummary]:
        """
        Search for products matching criteria.

        Args:
            query: Search terms (e.g., "black dress", "nike shoes")
            category: Filter by category (e.g., "dresses", "shoes")
            gender: Filter by gender ("men", "women", "unisex")
            min_price: Minimum price in INR
            max_price: Maximum price in INR
            limit: Maximum number of results to return

        Returns:
            List of matching products (lightweight summaries)
        """
        ...

    async def get_product(self, product_id: str) -> Product | None:
        """
        Get full product details by ID.

        Args:
            product_id: Unique product identifier from search results

        Returns:
            Full product details, or None if not found
        """
        ...

    async def get_trending(
        self,
        category: str | None = None,
        limit: int = 20,
    ) -> list[ProductSummary]:
        """
        Get trending/popular products.

        Args:
            category: Optional category filter
            limit: Maximum number of results

        Returns:
            List of trending products
        """
        ...

    async def close(self) -> None:
        """
        Clean up resources (HTTP clients, etc.).

        Should be called when done with the scraper.
        """
        ...

"""
Klydo MCP Server entry point.

This module defines the MCP server and tools for fashion discovery.
Run with: python -m klydo.server or use the `klydo` command.

Usage with Claude Desktop:
    Add to your claude_desktop_config.json:
    {
        "mcpServers": {
            "klydo": {
                "command": "uv",
                "args": ["--directory", "/path/to/klydo-mcp-server", "run", "klydo"]
            }
        }
    }
"""

from fastmcp import FastMCP

from klydo.config import settings
from klydo.models.product import Product, ProductSummary
from klydo.scrapers import get_scraper

# Initialize MCP server
mcp = FastMCP(
    name="Klydo Fashion",
    instructions="""
Fashion discovery assistant for Indian Gen Z (18-32 age group).

You can help users:
- Search for fashion products (clothes, shoes, accessories)
- Get detailed product information with images
- Find trending/popular fashion items

All products include:
- Direct purchase links to buy
- Multiple images
- Price with discounts
- Available sizes and colors

Tips for best results:
- Use specific search terms like "black cotton dress" or "nike running shoes"
- Filter by gender (men/women) for better results
- Use price filters to stay within budget
""",
)

# Get scraper instance
_scraper = get_scraper(settings.default_scraper)


@mcp.tool
async def search_products(
    query: str,
    category: str | None = None,
    gender: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    limit: int = 10,
) -> list[ProductSummary]:
    """
    Search for fashion products.

    Args:
        query: Search terms (e.g., "black dress", "nike shoes", "cotton kurta")
        category: Filter by category (e.g., "dresses", "shoes", "tshirts", "kurtas")
        gender: Filter by gender ("men" or "women")
        min_price: Minimum price in INR (e.g., 500)
        max_price: Maximum price in INR (e.g., 2000)
        limit: Maximum number of results (default 10, max 50)

    Returns:
        List of matching products with images, prices, and purchase links.

    Example:
        Search for "floral dress" with max price 1500 for women
    """
    return await _scraper.search(
        query=query,
        category=category,
        gender=gender,
        min_price=min_price,
        max_price=max_price,
        limit=min(limit, 50),
    )


@mcp.tool
async def get_product_details(product_id: str) -> Product | None:
    """
    Get complete product information including all images, sizes, and specifications.

    Args:
        product_id: The product ID from search results

    Returns:
        Full product details including:
        - All product images (multiple angles)
        - Available sizes
        - Available colors
        - Rating and reviews
        - Full description
        - Direct purchase link

        Returns None if product not found.

    Example:
        Get details for product ID "12345678"
    """
    return await _scraper.get_product(product_id)


@mcp.tool
async def get_trending(
    category: str | None = None,
    limit: int = 10,
) -> list[ProductSummary]:
    """
    Get currently trending/popular fashion products.

    Args:
        category: Optional category filter (e.g., "dresses", "shoes", "tshirts")
        limit: Maximum number of results (default 10, max 50)

    Returns:
        List of trending products sorted by popularity.

    Example:
        Get trending shoes, or just "get trending" for all categories
    """
    return await _scraper.get_trending(
        category=category,
        limit=min(limit, 50),
    )


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()

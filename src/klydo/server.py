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

import time

from fastmcp import FastMCP

from klydo.config import settings
from klydo.logging import logger, log_request, log_response
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
- Multiple images (CDN-hosted, directly viewable)
- Price with discounts
- Available sizes and colors
- Product page links (may not always be accessible)

IMPORTANT - When presenting products to users:
- ALWAYS show image URLs (image_url field) as the primary way to view products
- Image URLs are direct CDN links that are always accessible and viewable
- The 'url' field may contain product page links that aren't always accessible
- For product details, display ALL images from the 'images' array so users can see products from multiple angles
- Format image URLs as clickable/viewable links for easy access

Tips for best results:
- Use specific search terms like "black cotton dress" or "nike running shoes"
- Filter by gender (men/women) for better results
- Use price filters to stay within budget
""",
)

# Get scraper instance
_scraper = get_scraper(settings.default_scraper)

# Log server startup
logger.info(
    f"Klydo MCP Server initialized | scraper={settings.default_scraper} | debug={settings.debug}"
)


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
        List of matching products with:
        - image_url: Direct CDN link to product image (ALWAYS show this to users to view products)
        - price: Current price with discount information
        - brand: Product brand name
        - name: Product name and description
        - url: Product page link (may not always be accessible; prefer showing image_url)

        IMPORTANT: When presenting results to users, display the image_url as the primary
        way to view products. These are direct CDN links that are always accessible.

    Example:
        Search for "floral dress" with max price 1500 for women
    """
    start_time = time.time()
    log_request(
        "search_products",
        query=query,
        category=category,
        gender=gender,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
    )

    result = await _scraper.search(
        query=query,
        category=category,
        gender=gender,
        min_price=min_price,
        max_price=max_price,
        limit=min(limit, 50),
    )

    duration_ms = (time.time() - start_time) * 1000
    log_response("search_products", duration_ms, result_count=len(result))

    return result


@mcp.tool
async def get_product_details(product_id: str) -> Product | None:
    """
    Get complete product information including all images, sizes, and specifications.

    Args:
        product_id: The product ID from search results

    Returns:
        Full product details including:
        - images: Array of ALL product images from multiple angles (CRITICAL: Display ALL these image URLs to users)
        - image_url: Primary product image (also accessible)
        - Available sizes and colors
        - Rating and reviews
        - Full description
        - url: Product page link (may not be accessible; images are the primary viewing method)

        Returns None if product not found.

        CRITICAL FOR PRESENTATION:
        When showing product details to users, display ALL image URLs from the 'images' array.
        These are direct CDN links that are always accessible and allow users to view the
        product from multiple angles. The image URLs should be formatted as clickable/viewable
        links. Do NOT rely on the 'url' field for viewing products.

    Example:
        Get details for product ID "STL_HBIVEZLO78F27UG9AFRL"
    """
    start_time = time.time()
    log_request("get_product_details", product_id=product_id)

    result = await _scraper.get_product(product_id)

    duration_ms = (time.time() - start_time) * 1000
    log_response(
        "get_product_details",
        duration_ms,
        found=result is not None,
        product_id=product_id,
    )

    return result


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
        List of trending products sorted by popularity, each with:
        - image_url: Direct CDN link to product image (ALWAYS show this to users to view products)
        - price: Current price with discount information
        - brand: Product brand name
        - name: Product name and description
        - url: Product page link (may not always be accessible; prefer showing image_url)

        IMPORTANT: When presenting trending products to users, display the image_url as the
        primary way to view products. These are direct CDN links that are always accessible.

    Example:
        Get trending shoes, or just "get trending" for all categories
    """
    start_time = time.time()
    log_request("get_trending", category=category, limit=limit)

    result = await _scraper.get_trending(
        category=category,
        limit=min(limit, 50),
    )

    duration_ms = (time.time() - start_time) * 1000
    log_response("get_trending", duration_ms, result_count=len(result))

    return result


def main() -> None:
    """Run the MCP server."""
    logger.info("Starting Klydo MCP Server...")
    mcp.run()


if __name__ == "__main__":
    main()

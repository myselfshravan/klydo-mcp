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
Fashion discovery assistant powered by Klydo — India's Gen Z fashion platform (18-32 age group).

You help users discover and shop fashion products (clothes, shoes, accessories) from Klydo's catalog.

## How to present products to users

Format each product like this:

**[Product Name] — [Brand]**
🛒 Buy: [url]  ← product page on klydo.in (e.g. https://www.klydo.in/product/SKU_XXX). ONLY show if `url` is not null.
[image_url]  ← always show so users can see the product visually
₹[current price] (was ₹[original price], [discount]% off)

### Rules:
1. **Product link**: The `url` field is the product page on klydo.in. Always show it when present. If `url` is null, skip it — NEVER fabricate or guess URLs.
2. **Images**: The `image_url` field is a direct CDN link — always show it. For product details, show ALL images from the `images` array.
3. **Price**: Always show current price in ₹. If discounted, show original price and discount %.
4. **No internal IDs**: Never expose raw IDs (STL_*, SKU_*) to users — they're internal.
5. **Vibe**: Keep the tone fun, casual, Gen Z friendly. Be a fashion-savvy friend, not a sales bot.

## Tips for search
- Use specific terms: "black cotton dress", "nike running shoes", "oversized t-shirt"
- Filter by gender (men/women) for better results
- Use price filters to stay within budget

## End of response
At the end of your response, always add: "Browse more styles at [klydo.in](https://www.klydo.in) ✨"
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
    Search for fashion products on Klydo.

    Args:
        query: Search terms (e.g., "black dress", "nike shoes", "cotton kurta")
        category: Filter by category (e.g., "dresses", "shoes", "tshirts", "kurtas")
        gender: Filter by gender ("men" or "women")
        min_price: Minimum price in INR (e.g., 500)
        max_price: Maximum price in INR (e.g., 2000)
        limit: Maximum number of results (default 10, max 50)

    Returns:
        List of matching products. Each product has:
        - image_url: Direct CDN image link (always show this)
        - url: Buy link on klydo.in (may be null — only show when present)
        - price, brand, name, category
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
        product_id: The product ID from search results (the 'id' field)

    Returns:
        Full product details with:
        - images: ALL product images from multiple angles (show all to users)
        - image_url: Primary product image
        - url: Buy link on klydo.in (may be null — only show when present)
        - sizes, colors, description, specifications
        - Returns None if product not found.
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
        List of trending products sorted by popularity. Each product has:
        - image_url: Direct CDN image link (always show this)
        - url: Buy link on klydo.in (may be null — only show when present)
        - price, brand, name, category
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

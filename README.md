# Klydo MCP Server

Fashion discovery MCP server for Indian Gen Z (18-32 age group). Enables AI assistants like Claude to search and discover fashion products from Indian e-commerce sites.

## Features

- **Search Products**: Search fashion items with filters (category, gender, price range)
- **Product Details**: Get complete product info including images, sizes, colors, ratings
- **Trending Products**: Discover what's popular right now

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/klydo-mcp-server.git
cd klydo-mcp-server

# Install dependencies with uv
uv sync
```

### Usage with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "klydo": {
      "command": "uv",
      "args": ["--directory", "/path/to/klydo-mcp-server", "run", "klydo"]
    }
  }
}
```

Then restart Claude Desktop.

### Run Standalone

```bash
uv run klydo
```

## MCP Tools

### `search_products`

Search for fashion products.

**Parameters:**

- `query` (required): Search terms (e.g., "black dress", "nike shoes")
- `category`: Filter by category (e.g., "dresses", "shoes")
- `gender`: Filter by gender ("men" or "women")
- `min_price`: Minimum price in INR
- `max_price`: Maximum price in INR
- `limit`: Max results (default 10, max 50)

### `get_product_details`

Get complete product information.

**Parameters:**

- `product_id` (required): Product ID from search results

**Returns:** Full product details including all images, sizes, colors, ratings, and purchase link.

### `get_trending`

Get currently trending/popular fashion products.

**Parameters:**

- `category`: Optional category filter
- `limit`: Max results (default 10, max 50)

## Project Structure

```text
klydo-mcp-server/
├── src/klydo/
│   ├── __init__.py
│   ├── server.py          # MCP server entry point
│   ├── config.py          # Configuration (Pydantic Settings)
│   ├── models/
│   │   └── product.py     # Product, Price models
│   └── scrapers/
│       ├── base.py        # Scraper protocol (interface)
│       ├── cache.py       # File-based cache with TTL
│       └── myntra.py      # Myntra scraper implementation
├── pyproject.toml
├── .env.example
└── README.md
```

## Configuration

Copy `.env.example` to `.env` and customize:

```bash
KLYDO_DEFAULT_SCRAPER=myntra
KLYDO_REQUEST_TIMEOUT=30
KLYDO_CACHE_TTL=3600
KLYDO_DEBUG=false
```

## Adding New Scrapers

1. Create a new file in `src/klydo/scrapers/` (e.g., `ajio.py`)
2. Implement the `ScraperProtocol` interface:

```python
from klydo.scrapers.base import ScraperProtocol
from klydo.models.product import Product, ProductSummary

class AjioScraper:
    @property
    def source_name(self) -> str:
        return "Ajio"

    async def search(self, query: str, **filters) -> list[ProductSummary]:
        # Implementation
        ...

    async def get_product(self, product_id: str) -> Product | None:
        # Implementation
        ...

    async def get_trending(self, **filters) -> list[ProductSummary]:
        # Implementation
        ...

    async def close(self) -> None:
        # Cleanup
        ...
```

3. Register in `src/klydo/scrapers/__init__.py`:

```python
_SCRAPERS = {
    "myntra": MyntraScraper,
    "ajio": AjioScraper,  # Add here
}
```

## Development

```bash
# Install dev dependencies
uv sync --dev

# Run tests
uv run pytest
```

## License

MIT

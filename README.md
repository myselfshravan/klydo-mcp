# Klydo MCP Server

[![CI](https://github.com/myselfshravan/klydo-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/myselfshravan/klydo-mcp/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/klydo-mcp-server.svg)](https://badge.fury.io/py/klydo-mcp-server)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

**Fashion discovery MCP server for Indian Gen Z (18-32 age group).** 

Enables AI assistants like Claude to search and discover fashion products from Indian e-commerce sites. Built by [Klydo](https://klydo.in) — a Bangalore-based startup for Gen-Z quick tech fashion commerce.

## ✨ Features

- 🔍 **Search Products** — Search fashion items with filters (category, gender, price range)
- 📦 **Product Details** — Get complete product info including images, sizes, colors, ratings
- 🔥 **Trending Products** — Discover what's popular right now
- 🛒 **Sources** — Built-in scrapers for Myntra and the Klydo brand (klydo.in)
- 📝 **Structured Logging** — Debug-friendly logs with Loguru
- ⚡ **Fast & Cached** — In-memory caching for quick responses

## 🚀 Quick Start

### Installation

#### Option 1: Install from PyPI (Recommended)

```bash
# Using pip
pip install klydo-mcp-server

# Or using pipx (isolated environment)
pipx install klydo-mcp-server

# Or using uvx (no installation needed)
uvx klydo-mcp-server
```

#### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/myselfshravan/klydo-mcp.git
cd klydo-mcp

# Install dependencies with uv
uv sync
```

### Usage with Claude Desktop

#### If installed via PyPI (pip/pipx)

Add to your Claude Desktop configuration:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "klydo": {
      "command": "klydo"
    }
  }
}
```

#### If using uvx (recommended for easy updates)

```json
{
  "mcpServers": {
    "klydo": {
      "command": "uvx",
      "args": ["klydo-mcp-server"]
    }
  }
}
```

#### If installed from source

```json
{
  "mcpServers": {
    "klydo": {
      "command": "uv",
      "args": ["--directory", "/path/to/klydo-mcp", "run", "klydo"]
    }
  }
}
```

Then restart Claude Desktop.

### Run Standalone

```bash
uv run klydo
```

## 🛠️ MCP Tools

### `search_products`

Search for fashion products.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | ✅ | Search terms (e.g., "black dress", "nike shoes") |
| `category` | string | ❌ | Filter by category (e.g., "dresses", "shoes") |
| `gender` | string | ❌ | Filter by gender ("men" or "women") |
| `min_price` | int | ❌ | Minimum price in INR |
| `max_price` | int | ❌ | Maximum price in INR |
| `limit` | int | ❌ | Max results (default 10, max 50) |

### `get_product_details`

Get complete product information.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `product_id` | string | ✅ | Product ID from search results |

**Returns:** Full product details including all images, sizes, colors, ratings, and purchase link.

### `get_trending`

Get currently trending/popular fashion products.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | ❌ | Category filter |
| `limit` | int | ❌ | Max results (default 10, max 50) |

## ⚙️ Configuration

Copy `.env.example` to `.env` and customize:

```bash
# Default scraper: "klydo" or "myntra"
KLYDO_DEFAULT_SCRAPER=klydo

# Request settings
KLYDO_REQUEST_TIMEOUT=30
KLYDO_CACHE_TTL=3600

# Debug mode (set to false in production)
KLYDO_DEBUG=false

# API token for klydo.in scraper (required for Klydo scraper)
KLYDO_KLYDO_API_TOKEN=your-token
```

## 📁 Project Structure

```text
klydo-mcp/
├── src/klydo/
│   ├── __init__.py
│   ├── server.py          # MCP server entry point
│   ├── config.py          # Configuration (Pydantic Settings)
│   ├── logging.py         # Loguru configuration
│   ├── models/
│   │   └── product.py     # Product, Price models
│   └── scrapers/
│       ├── base.py        # Scraper protocol (interface)
│       ├── cache.py       # In-memory cache with TTL
│       ├── klydo_store.py # Klydo.in scraper
│       └── myntra.py      # Myntra scraper
├── tests/                 # Test suite
├── .github/workflows/     # CI/CD pipelines
├── pyproject.toml
└── README.md
```

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_models.py
```

## 🔧 Development

```bash
# Install dev dependencies
uv sync --dev

# Run linting
uv run ruff check src/

# Format code
uv run ruff format src/

# Run the server locally
uv run klydo
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🔐 Security

For security issues, please see our [Security Policy](SECURITY.md).

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 🏢 About Klydo

[Klydo](https://klydo.in) is a Bangalore-based startup building quick tech fashion commerce for Gen-Z. This MCP server is part of our mission to make fashion discovery seamless across AI interfaces.

---

**Made with ❤️ in Bangalore, India**
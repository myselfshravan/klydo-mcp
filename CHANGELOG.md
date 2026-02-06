# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Structured logging with Loguru for better debugging and monitoring
- Production-ready environment configuration (`.env.production.example`)
- Comprehensive test suite with pytest
- GitHub Actions CI/CD pipeline for testing and publishing
- CHANGELOG.md for tracking changes
- CONTRIBUTING.md with contribution guidelines
- SECURITY.md with security policy

### Changed
- Removed hardcoded DEFAULT_AUTH_TOKEN for better security
- Updated project URLs to point to official GitHub repository
- Updated author information in pyproject.toml

### Security
- API tokens must now be provided via environment variables only
- No hardcoded secrets in codebase

## [0.1.0] - 2026-06-02

### Added
- Initial release of Klydo MCP Server
- MCP server implementation using FastMCP
- Klydo.in catalog API integration
- Product search with filters (category, gender, price range)
- Product details retrieval with images and specifications
- Trending products discovery
- In-memory caching for API responses
- Pydantic models for type-safe data handling
- Configuration via environment variables
- Claude Desktop integration support

### Features
- `search_products` - Search for fashion products with various filters
- `get_product_details` - Get complete product information
- `get_trending` - Get trending/popular products

### Technical
- Python 3.11+ support
- Async HTTP client with httpx
- pydantic-settings for configuration management
- Installable via pip/uv from PyPI

[Unreleased]: https://github.com/myselfshravan/klydo-mcp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/myselfshravan/klydo-mcp/releases/tag/v0.1.0
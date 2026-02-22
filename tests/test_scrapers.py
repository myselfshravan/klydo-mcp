"""
Tests for scraper implementations.

These tests use mocked HTTP responses to test scraper logic without
making real API calls.
"""

from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

from klydo.scrapers.klydo_store import KlydoStoreScraper


class TestKlydoStoreScraper:
    """Tests for the KlydoStoreScraper."""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance."""
        return KlydoStoreScraper()

    def test_scraper_source_name(self, scraper: KlydoStoreScraper):
        """Test scraper source name property."""
        assert scraper.source_name == "Klydo"

    def test_session_id_generation(self, scraper: KlydoStoreScraper):
        """Test that session ID is generated."""
        assert scraper._session_id is not None
        assert len(scraper._session_id) > 0
        assert "-" in scraper._session_id

    def test_build_product_url_with_slug(self, scraper: KlydoStoreScraper):
        """Test URL building with slug."""
        url = scraper._build_product_url("cotton-tshirt")
        assert url == "https://www.klydo.in/p/cotton-tshirt"

    def test_build_product_url_no_slug_no_sku(self, scraper: KlydoStoreScraper):
        """Test URL returns None when no slug or SKU ID available."""
        url = scraper._build_product_url(None)
        assert url is None

    def test_build_product_url_with_sku(self, scraper: KlydoStoreScraper):
        """Test URL building with SKU ID."""
        url = scraper._build_product_url(None, sku_id="SKU_ABC")
        assert url == "https://www.klydo.in/product/SKU_ABC"

    def test_build_product_url_slug_takes_priority(self, scraper: KlydoStoreScraper):
        """Test that slug takes priority over SKU ID."""
        url = scraper._build_product_url("cotton-tshirt", sku_id="SKU_ABC")
        assert url == "https://www.klydo.in/p/cotton-tshirt"

    def test_to_rupees_conversion(self, scraper: KlydoStoreScraper):
        """Test paisa to rupees conversion."""
        assert scraper._to_rupees(99900) == Decimal("999")
        assert scraper._to_rupees(149900) == Decimal("1499")
        assert scraper._to_rupees(50) == Decimal("0.50")

    def test_to_rupees_invalid_value(self, scraper: KlydoStoreScraper):
        """Test conversion with invalid value."""
        assert scraper._to_rupees(None) == Decimal("0")
        assert scraper._to_rupees("invalid") == Decimal("0")

    def test_discount_percent_calculation(self, scraper: KlydoStoreScraper):
        """Test discount percentage calculation."""
        # When discount is provided
        assert scraper._discount_percent(Decimal("999"), Decimal("1499"), 33) == 33

        # When discount needs to be calculated
        result = scraper._discount_percent(Decimal("999"), Decimal("1499"), None)
        assert result == 33  # (1499-999)/1499 * 100 ≈ 33%

    def test_discount_percent_no_discount(self, scraper: KlydoStoreScraper):
        """Test discount when price equals MRP."""
        result = scraper._discount_percent(Decimal("999"), Decimal("999"), None)
        assert result is None

    def test_parse_product_summary(
        self, scraper: KlydoStoreScraper, sample_api_search_response: dict
    ):
        """Test parsing product summary from API response."""
        item = sample_api_search_response["products"][0]
        summary = scraper._parse_product_summary(item)

        assert summary is not None
        assert summary.id == "STL_ABC123"
        assert summary.name == "Cotton T-Shirt"
        assert summary.brand == "Klydo"
        assert summary.price.current == Decimal("999")
        assert summary.price.original == Decimal("1499")
        assert summary.category == "T-Shirts"
        assert summary.source == "Klydo"

    def test_parse_product_summary_missing_data(self, scraper: KlydoStoreScraper):
        """Test parsing with missing required fields."""
        # Missing styleId
        result = scraper._parse_product_summary(
            {"imageUrl": "https://example.com/img.jpg"}
        )
        assert result is None

        # Missing imageUrl
        result = scraper._parse_product_summary({"styleId": "STL_123"})
        assert result is None

    def test_parse_product_detail(
        self, scraper: KlydoStoreScraper, sample_api_product_response: dict
    ):
        """Test parsing full product from API response."""
        product = scraper._parse_product_detail(
            sample_api_product_response,
            "STL_ABC123",
        )

        assert product is not None
        assert product.id == "STL_ABC123"
        assert product.name == "Cotton T-Shirt"
        assert product.brand == "Klydo"
        assert product.description == "Premium cotton t-shirt"
        assert len(product.images) == 2
        assert "S" in product.sizes
        assert "M" in product.sizes
        assert "L" not in product.sizes  # L is not available
        assert "Material" in product.specifications
        assert product.colors == ["Black"]

    @pytest.mark.asyncio
    async def test_search_with_cache_hit(
        self, scraper: KlydoStoreScraper, sample_api_search_response: dict
    ):
        """Test search returns cached results."""
        # Mock cache to return data
        cached_data = [
            {
                "id": "STL_CACHED",
                "name": "Cached Product",
                "brand": "Klydo",
                "price": {"current": "500", "currency": "INR"},
                "image_url": "https://cdn.klydo.in/img.jpg",
                "category": "T-Shirts",
                "source": "Klydo",
                "url": "https://www.klydo.in/p/cached",
            }
        ]

        with patch.object(scraper._cache, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = cached_data

            with patch.object(scraper._cache, "set", new_callable=AsyncMock):
                results = await scraper.search("t-shirt")

        assert len(results) == 1
        assert results[0].id == "STL_CACHED"

    @pytest.mark.asyncio
    async def test_search_api_error_returns_empty(self, scraper: KlydoStoreScraper):
        """Test that API errors return empty list."""
        import httpx

        with patch.object(scraper._cache, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None  # Cache miss

            with patch.object(
                scraper._client, "get", new_callable=AsyncMock
            ) as mock_client:
                mock_client.side_effect = httpx.HTTPError("Connection failed")

                results = await scraper.search("t-shirt")

        assert results == []

    @pytest.mark.asyncio
    async def test_close_client(self, scraper: KlydoStoreScraper):
        """Test that close properly closes the HTTP client."""
        with patch.object(
            scraper._client, "aclose", new_callable=AsyncMock
        ) as mock_close:
            await scraper.close()
            mock_close.assert_called_once()


class TestScraperFactory:
    """Tests for the scraper factory function."""

    def test_get_klydo_scraper(self):
        """Test getting Klydo scraper."""
        from klydo.scrapers import get_scraper

        scraper = get_scraper("klydo")
        assert scraper.source_name == "Klydo"

    def test_get_myntra_scraper(self):
        """Test getting Myntra scraper."""
        from klydo.scrapers import get_scraper

        scraper = get_scraper("myntra")
        assert scraper.source_name == "Myntra"

    def test_get_invalid_scraper(self):
        """Test getting invalid scraper raises error."""
        from klydo.scrapers import get_scraper

        with pytest.raises(ValueError, match="Unknown scraper"):
            get_scraper("invalid-scraper")

    def test_list_scrapers(self):
        """Test listing available scrapers."""
        from klydo.scrapers import list_scrapers

        scrapers = list_scrapers()
        assert "klydo" in scrapers
        assert "myntra" in scrapers

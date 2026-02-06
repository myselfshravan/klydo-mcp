"""
Pytest configuration and shared fixtures.

This module provides common fixtures used across all tests.
"""

from decimal import Decimal

import pytest

from klydo.models.product import Price, Product, ProductImage, ProductSummary


@pytest.fixture
def sample_price() -> Price:
    """Create a sample price with discount."""
    return Price(
        current=Decimal("999"),
        original=Decimal("1499"),
        currency="INR",
        discount_percent=33,
    )


@pytest.fixture
def sample_price_no_discount() -> Price:
    """Create a sample price without discount."""
    return Price(
        current=Decimal("799"),
        currency="INR",
    )


@pytest.fixture
def sample_product_summary(sample_price: Price) -> ProductSummary:
    """Create a sample product summary."""
    return ProductSummary(
        id="STL_TEST123",
        name="Classic Black T-Shirt",
        brand="Klydo",
        price=sample_price,
        image_url="https://cdn.klydo.in/images/test-product.jpg",
        category="T-Shirts",
        source="Klydo",
        url="https://www.klydo.in/p/classic-black-tshirt",
    )


@pytest.fixture
def sample_product(sample_price: Price) -> Product:
    """Create a sample full product."""
    return Product(
        id="STL_TEST123",
        name="Classic Black T-Shirt",
        brand="Klydo",
        price=sample_price,
        image_url="https://cdn.klydo.in/images/test-product.jpg",
        category="T-Shirts",
        source="Klydo",
        url="https://www.klydo.in/p/classic-black-tshirt",
        description="A comfortable cotton t-shirt perfect for everyday wear.",
        images=[
            ProductImage(
                url="https://cdn.klydo.in/images/test-product-1.jpg",
                alt="Front view",
            ),
            ProductImage(
                url="https://cdn.klydo.in/images/test-product-2.jpg",
                alt="Back view",
            ),
        ],
        sizes=["S", "M", "L", "XL"],
        colors=["Black", "Navy", "White"],
        rating=4.5,
        review_count=128,
        in_stock=True,
        specifications={
            "Material": "100% Cotton",
            "Fit": "Regular",
            "Wash Care": "Machine Wash",
        },
    )


@pytest.fixture
def sample_api_search_response() -> dict:
    """Sample API response for search endpoint."""
    return {
        "products": [
            {
                "styleId": "STL_ABC123",
                "title": "Cotton T-Shirt",
                "brand": "Klydo",
                "imageUrl": "https://cdn.klydo.in/images/1.jpg",
                "sellingPrice": 99900,  # In paisa (999 INR)
                "mrp": 149900,  # In paisa (1499 INR)
                "discountPercentage": 33,
                "category": "T-Shirts",
                "slug": "cotton-tshirt",
            },
            {
                "styleId": "STL_DEF456",
                "title": "Polo Shirt",
                "brand": "Klydo",
                "imageUrl": "https://cdn.klydo.in/images/2.jpg",
                "sellingPrice": 129900,
                "mrp": 179900,
                "discountPercentage": 28,
                "category": "Shirts",
                "slug": "polo-shirt",
            },
        ],
        "totalCount": 2,
    }


@pytest.fixture
def sample_api_product_response() -> dict:
    """Sample API response for product detail endpoint."""
    return {
        "styleId": "STL_ABC123",
        "title": "Cotton T-Shirt",
        "brandName": "Klydo",
        "description": "Premium cotton t-shirt",
        "slug": "cotton-tshirt",
        "media": [
            {"url": "https://cdn.klydo.in/images/1a.jpg"},
            {"url": "https://cdn.klydo.in/images/1b.jpg"},
        ],
        "sizes": [
            {
                "skuId": "SKU_001",
                "size": "S",
                "sellingPrice": 99900,
                "mrp": 149900,
                "inventory": {"available": True},
            },
            {
                "skuId": "SKU_002",
                "size": "M",
                "sellingPrice": 99900,
                "mrp": 149900,
                "inventory": {"available": True},
            },
            {
                "skuId": "SKU_003",
                "size": "L",
                "sellingPrice": 99900,
                "mrp": 149900,
                "inventory": {"available": False},
            },
        ],
        "specifications": [
            {"name": "Material", "value": "Cotton"},
            {"name": "Fit", "value": "Regular"},
        ],
        "label": "Black",
    }
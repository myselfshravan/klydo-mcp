"""
Product models for fashion e-commerce.

These models define the structure of product data returned
by scrapers and exposed through MCP tools.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field, HttpUrl


class ProductImage(BaseModel):
    """
    Product image with URL and alt text.

    Attributes:
        url: Direct URL to the image
        alt: Alt text for accessibility
    """

    url: HttpUrl
    alt: str = ""


class Price(BaseModel):
    """
    Price with optional discount information.

    Attributes:
        current: Current selling price
        original: Original price before discount (if applicable)
        currency: Currency code (default INR)
        discount_percent: Discount percentage (if applicable)
    """

    current: Decimal
    original: Decimal | None = None
    currency: str = "INR"
    discount_percent: int | None = None

    @property
    def has_discount(self) -> bool:
        """Check if product is discounted."""
        return self.original is not None and self.original > self.current


class ProductSummary(BaseModel):
    """
    Lightweight product for search results.

    Contains enough info to display in a list without
    fetching full product details.

    Attributes:
        id: Unique product identifier (from source site)
        name: Product name/title
        brand: Brand name
        price: Price information
        image_url: Primary product image URL
        category: Product category
        source: Scraper source name (e.g., 'myntra')
        url: Direct link to product page for purchase
    """

    id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name/title")
    brand: str = Field(..., description="Brand name")
    price: Price = Field(..., description="Price information")
    image_url: HttpUrl = Field(..., description="Primary product image URL")
    category: str = Field(..., description="Product category")
    source: str = Field(..., description="Scraper source (e.g., 'myntra')")
    url: HttpUrl = Field(..., description="Direct link to product page")


class Product(ProductSummary):
    """
    Full product details.

    Extends ProductSummary with complete information including
    all images, sizes, colors, ratings, and specifications.

    Attributes:
        description: Full product description
        images: All product images
        sizes: Available sizes
        colors: Available colors
        rating: Average rating (0-5)
        review_count: Number of reviews
        in_stock: Whether product is in stock
        specifications: Additional product specifications
    """

    description: str = Field(..., description="Full product description")
    images: list[ProductImage] = Field(
        default_factory=list, description="All product images"
    )
    sizes: list[str] = Field(default_factory=list, description="Available sizes")
    colors: list[str] = Field(default_factory=list, description="Available colors")
    rating: float | None = Field(None, ge=0, le=5, description="Average rating (0-5)")
    review_count: int = Field(default=0, ge=0, description="Number of reviews")
    in_stock: bool = Field(default=True, description="Whether product is in stock")
    specifications: dict[str, str] = Field(
        default_factory=dict, description="Additional product specifications"
    )

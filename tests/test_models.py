"""
Tests for Pydantic models.

These tests validate the data models used throughout the application.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from klydo.models.product import Price, Product, ProductImage, ProductSummary


class TestPrice:
    """Tests for the Price model."""

    def test_price_creation_with_all_fields(self):
        """Test creating a price with all fields."""
        price = Price(
            current=Decimal("999"),
            original=Decimal("1499"),
            currency="INR",
            discount_percent=33,
        )
        assert price.current == Decimal("999")
        assert price.original == Decimal("1499")
        assert price.currency == "INR"
        assert price.discount_percent == 33

    def test_price_creation_minimal(self):
        """Test creating a price with only required fields."""
        price = Price(current=Decimal("500"))
        assert price.current == Decimal("500")
        assert price.original is None
        assert price.currency == "INR"  # Default
        assert price.discount_percent is None

    def test_price_has_discount_property(self, sample_price: Price):
        """Test the has_discount computed property."""
        assert sample_price.has_discount is True

    def test_price_no_discount_property(self, sample_price_no_discount: Price):
        """Test has_discount returns False when no original price."""
        assert sample_price_no_discount.has_discount is False

    def test_price_same_original_no_discount(self):
        """Test has_discount when original equals current."""
        price = Price(
            current=Decimal("500"),
            original=Decimal("500"),
        )
        assert price.has_discount is False

    def test_price_from_int(self):
        """Test creating price from integer values."""
        price = Price(current=999, original=1499)
        assert price.current == Decimal("999")
        assert price.original == Decimal("1499")

    def test_price_from_float(self):
        """Test creating price from float values."""
        price = Price(current=999.50, original=1499.99)
        assert price.current == Decimal("999.50")
        assert price.original == Decimal("1499.99")


class TestProductImage:
    """Tests for the ProductImage model."""

    def test_product_image_creation(self):
        """Test creating a product image."""
        image = ProductImage(
            url="https://cdn.klydo.in/images/test.jpg",
            alt="Test product image",
        )
        assert str(image.url) == "https://cdn.klydo.in/images/test.jpg"
        assert image.alt == "Test product image"

    def test_product_image_default_alt(self):
        """Test default alt text."""
        image = ProductImage(url="https://cdn.klydo.in/images/test.jpg")
        assert image.alt == ""

    def test_product_image_invalid_url(self):
        """Test that invalid URLs are rejected."""
        with pytest.raises(ValidationError):
            ProductImage(url="not-a-valid-url")


class TestProductSummary:
    """Tests for the ProductSummary model."""

    def test_product_summary_creation(self, sample_product_summary: ProductSummary):
        """Test creating a product summary."""
        assert sample_product_summary.id == "STL_TEST123"
        assert sample_product_summary.name == "Classic Black T-Shirt"
        assert sample_product_summary.brand == "Klydo"
        assert sample_product_summary.category == "T-Shirts"
        assert sample_product_summary.source == "Klydo"

    def test_product_summary_has_valid_url(
        self, sample_product_summary: ProductSummary
    ):
        """Test that product summary has a valid URL."""
        assert str(sample_product_summary.url).startswith("https://")

    def test_product_summary_has_valid_image_url(
        self, sample_product_summary: ProductSummary
    ):
        """Test that product summary has a valid image URL."""
        assert str(sample_product_summary.image_url).startswith("https://")

    def test_product_summary_serialization(
        self, sample_product_summary: ProductSummary
    ):
        """Test that product summary can be serialized to dict."""
        data = sample_product_summary.model_dump()
        assert data["id"] == "STL_TEST123"
        assert data["name"] == "Classic Black T-Shirt"
        assert "price" in data

    def test_product_summary_json_serialization(
        self, sample_product_summary: ProductSummary
    ):
        """Test that product summary can be serialized to JSON."""
        json_str = sample_product_summary.model_dump_json()
        assert "STL_TEST123" in json_str
        assert "Classic Black T-Shirt" in json_str


class TestProduct:
    """Tests for the full Product model."""

    def test_product_creation(self, sample_product: Product):
        """Test creating a full product."""
        assert sample_product.id == "STL_TEST123"
        assert (
            sample_product.description
            == "A comfortable cotton t-shirt perfect for everyday wear."
        )
        assert len(sample_product.images) == 2
        assert sample_product.sizes == ["S", "M", "L", "XL"]
        assert sample_product.colors == ["Black", "Navy", "White"]
        assert sample_product.rating == 4.5
        assert sample_product.review_count == 128
        assert sample_product.in_stock is True

    def test_product_extends_summary(self, sample_product: Product):
        """Test that Product inherits from ProductSummary."""
        assert isinstance(sample_product, ProductSummary)
        assert sample_product.name == "Classic Black T-Shirt"
        assert sample_product.brand == "Klydo"

    def test_product_specifications(self, sample_product: Product):
        """Test product specifications dictionary."""
        assert sample_product.specifications["Material"] == "100% Cotton"
        assert sample_product.specifications["Fit"] == "Regular"

    def test_product_rating_validation(self):
        """Test that rating must be between 0 and 5."""
        with pytest.raises(ValidationError):
            Product(
                id="TEST",
                name="Test",
                brand="Test",
                price=Price(current=100),
                image_url="https://example.com/img.jpg",
                category="Test",
                source="Test",
                url="https://example.com/product",
                description="Test",
                rating=6.0,  # Invalid: > 5
            )

    def test_product_negative_rating_validation(self):
        """Test that rating cannot be negative."""
        with pytest.raises(ValidationError):
            Product(
                id="TEST",
                name="Test",
                brand="Test",
                price=Price(current=100),
                image_url="https://example.com/img.jpg",
                category="Test",
                source="Test",
                url="https://example.com/product",
                description="Test",
                rating=-1.0,  # Invalid: < 0
            )

    def test_product_review_count_validation(self):
        """Test that review_count cannot be negative."""
        with pytest.raises(ValidationError):
            Product(
                id="TEST",
                name="Test",
                brand="Test",
                price=Price(current=100),
                image_url="https://example.com/img.jpg",
                category="Test",
                source="Test",
                url="https://example.com/product",
                description="Test",
                review_count=-1,  # Invalid: < 0
            )

    def test_product_default_values(self):
        """Test default values for optional fields."""
        product = Product(
            id="TEST",
            name="Test Product",
            brand="Test Brand",
            price=Price(current=100),
            image_url="https://example.com/img.jpg",
            category="Test",
            source="Test",
            url="https://example.com/product",
            description="Test description",
        )
        assert product.images == []
        assert product.sizes == []
        assert product.colors == []
        assert product.rating is None
        assert product.review_count == 0
        assert product.in_stock is True
        assert product.specifications == {}

    def test_product_serialization_roundtrip(self, sample_product: Product):
        """Test that product can be serialized and deserialized."""
        json_str = sample_product.model_dump_json()
        restored = Product.model_validate_json(json_str)
        assert restored.id == sample_product.id
        assert restored.name == sample_product.name
        assert len(restored.images) == len(sample_product.images)

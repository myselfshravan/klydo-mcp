"""
Myntra scraper implementation.

Myntra is one of India's largest fashion e-commerce platforms.
This scraper uses their internal API endpoints to fetch product data.

Note: This is for educational/personal use. Respect robots.txt
and rate limits when using this scraper.
"""

import json
import re
from decimal import Decimal
from urllib.parse import quote_plus

import httpx
from selectolax.parser import HTMLParser

from klydo.config import settings
from klydo.models.product import Price, Product, ProductImage, ProductSummary
from klydo.scrapers.cache import Cache


def _extract_json_object(text: str, start_marker: str) -> dict | None:
    """
    Extract a complete JSON object from text starting at marker.

    Uses brace counting to find matching closing brace,
    handling nested objects and strings correctly.

    Args:
        text: Full text to search
        start_marker: String that precedes the JSON object

    Returns:
        Parsed JSON dict, or None if extraction fails
    """
    start = text.find(start_marker)
    if start == -1:
        return None

    # Find the start of the JSON object
    json_start = text.find("{", start)
    if json_start == -1:
        return None

    # Count braces to find the matching closing brace
    depth = 0
    in_string = False
    escape = False

    for i, char in enumerate(text[json_start:]):
        if escape:
            escape = False
            continue
        if char == "\\" and in_string:
            escape = True
            continue
        if char == '"' and not escape:
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                json_str = text[json_start : json_start + i + 1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    return None

    return None


class MyntraScraper:
    """
    Scraper for myntra.com.

    Uses Myntra's internal search API and product pages
    to fetch fashion product data.

    Attributes:
        source_name: Returns 'Myntra'
    """

    BASE_URL = "https://www.myntra.com"

    def __init__(self) -> None:
        """Initialize scraper with HTTP client and cache."""
        self._client = httpx.AsyncClient(
            headers=self._get_headers(),
            timeout=settings.request_timeout,
            follow_redirects=True,
        )
        self._cache = Cache(namespace="myntra", default_ttl=settings.cache_ttl)

    @property
    def source_name(self) -> str:
        """Human-readable source name."""
        return "Myntra"

    def _get_headers(self) -> dict[str, str]:
        """
        Get browser-like headers to avoid blocks.

        Returns:
            Headers dict for HTTP requests
        """
        return {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    async def search(
        self,
        query: str,
        *,
        category: str | None = None,
        gender: str | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        limit: int = 20,
    ) -> list[ProductSummary]:
        """
        Search Myntra products.

        Args:
            query: Search terms
            category: Optional category filter
            gender: Optional gender filter (men/women)
            min_price: Minimum price in INR
            max_price: Maximum price in INR
            limit: Max results to return

        Returns:
            List of matching products
        """
        # Build cache key
        cache_key = self._cache.cache_key(
            "search",
            query,
            category or "",
            gender or "",
            str(min_price or ""),
            str(max_price or ""),
        )

        # Check cache
        cached = await self._cache.get(cache_key)
        if cached:
            products = [ProductSummary.model_validate(p) for p in cached]
            return products[:limit]

        # Build search URL
        search_path = self._build_search_path(query, gender, category)
        url = f"{self.BASE_URL}/{search_path}"

        try:
            response = await self._client.get(url)
            response.raise_for_status()

            products = self._parse_search_results(response.text, limit)

            # Apply price filters
            if min_price is not None:
                products = [p for p in products if p.price.current >= min_price]
            if max_price is not None:
                products = [p for p in products if p.price.current <= max_price]

            # Cache results
            await self._cache.set(
                cache_key,
                [p.model_dump(mode="json") for p in products],
            )

            return products[:limit]

        except httpx.HTTPError as e:
            # Log error in debug mode
            if settings.debug:
                print(f"Search error: {e}")
            return []

    def _build_search_path(
        self,
        query: str,
        gender: str | None = None,
        category: str | None = None,
    ) -> str:
        """
        Build Myntra search URL path.

        Args:
            query: Search query
            gender: Gender filter
            category: Category filter

        Returns:
            URL path for search
        """
        # Myntra uses URL-based filtering
        parts = []

        if gender:
            parts.append(gender.lower())

        if category:
            parts.append(category.lower().replace(" ", "-"))

        # Add query
        encoded_query = quote_plus(query.lower().replace(" ", "-"))
        parts.append(encoded_query)

        return "-".join(parts) if parts else encoded_query

    def _parse_search_results(
        self,
        html: str,
        limit: int,
    ) -> list[ProductSummary]:
        """
        Parse search results from HTML.

        Myntra embeds product data in a script tag as JSON.

        Args:
            html: Raw HTML response
            limit: Max products to parse

        Returns:
            List of parsed products
        """
        products: list[ProductSummary] = []

        # Try to extract JSON data from script tag
        # Myntra stores product data in window.__myx
        data = _extract_json_object(html, "window.__myx")

        if data:
            try:
                search_data = data.get("searchData", {})
                results = search_data.get("results", {})
                product_list = results.get("products", [])

                for item in product_list[:limit]:
                    product = self._parse_product_from_json(item)
                    if product:
                        products.append(product)

                if products:
                    return products

            except (KeyError, TypeError):
                pass

        # Fallback: parse HTML directly
        parser = HTMLParser(html)

        for item in parser.css("li.product-base")[:limit]:
            product = self._parse_product_from_html(item)
            if product:
                products.append(product)

        return products

    def _parse_product_from_json(self, data: dict) -> ProductSummary | None:
        """
        Parse product from Myntra JSON data.

        Args:
            data: Product JSON from Myntra

        Returns:
            ProductSummary or None if parsing fails
        """
        try:
            product_id = str(data.get("productId", ""))
            if not product_id:
                return None

            # Extract price
            price_data = data.get("price", data.get("mrp", 0))
            mrp = data.get("mrp", price_data)
            discount = data.get("discount", 0)

            # Handle price as int or dict
            if isinstance(price_data, dict):
                current_price = Decimal(str(price_data.get("discounted", price_data.get("mrp", 0))))
                original_price = Decimal(str(price_data.get("mrp", current_price)))
            else:
                current_price = Decimal(str(price_data))
                original_price = Decimal(str(mrp)) if mrp != price_data else None

            # Calculate discount percent from prices (discount field is amount, not percent)
            discount_percent = None
            if original_price and original_price > current_price:
                discount_percent = int(
                    ((original_price - current_price) / original_price) * 100
                )

            # Get image URL
            images = data.get("images", [])
            image_url = ""
            if images:
                img = images[0] if isinstance(images[0], dict) else {"src": images[0]}
                image_url = img.get("src", "")
                if not image_url.startswith("http"):
                    image_url = f"https://assets.myntassets.com/h_720,q_90,w_540/{image_url}"

            # Fallback to search image
            if not image_url:
                image_url = data.get("searchImage", "")
                if image_url and not image_url.startswith("http"):
                    image_url = f"https://assets.myntassets.com/h_720,q_90,w_540/{image_url}"

            if not image_url:
                return None

            # Extract category - can be string or dict with typeName
            article_type = data.get("articleType", data.get("category", "Fashion"))
            if isinstance(article_type, dict):
                category = article_type.get("typeName", "Fashion")
            else:
                category = str(article_type) if article_type else "Fashion"

            return ProductSummary(
                id=product_id,
                name=data.get("productName", data.get("product", "Unknown")),
                brand=data.get("brand", "Unknown"),
                price=Price(
                    current=current_price,
                    original=original_price,
                    currency="INR",
                    discount_percent=discount_percent,
                ),
                image_url=image_url,
                category=category,
                source=self.source_name,
                url=f"{self.BASE_URL}/{product_id}",
            )

        except (KeyError, ValueError, TypeError) as e:
            if settings.debug:
                print(f"Parse error: {e}")
            return None

    def _parse_product_from_html(self, element) -> ProductSummary | None:
        """
        Parse product from HTML element (fallback).

        Args:
            element: selectolax Node

        Returns:
            ProductSummary or None if parsing fails
        """
        try:
            # Get product link
            link = element.css_first("a")
            if not link:
                return None

            href = link.attributes.get("href", "")
            product_id = href.split("/")[-1] if href else ""

            if not product_id:
                return None

            # Get image
            img = element.css_first("img")
            image_url = ""
            if img:
                image_url = img.attributes.get("src", img.attributes.get("data-src", ""))

            if not image_url:
                return None

            # Get brand
            brand_elem = element.css_first(".product-brand")
            brand = brand_elem.text().strip() if brand_elem else "Unknown"

            # Get name
            name_elem = element.css_first(".product-product")
            name = name_elem.text().strip() if name_elem else "Unknown Product"

            # Get price
            price_elem = element.css_first(".product-discountedPrice")
            if not price_elem:
                price_elem = element.css_first(".product-price")

            current_price = Decimal("0")
            if price_elem:
                price_text = price_elem.text().strip()
                # Extract numbers from price text (e.g., "Rs. 1,299" -> 1299)
                price_match = re.search(r"[\d,]+", price_text)
                if price_match:
                    current_price = Decimal(price_match.group().replace(",", ""))

            # Get original price
            original_elem = element.css_first(".product-strike")
            original_price = None
            if original_elem:
                original_text = original_elem.text().strip()
                price_match = re.search(r"[\d,]+", original_text)
                if price_match:
                    original_price = Decimal(price_match.group().replace(",", ""))

            # Get discount
            discount_percent = None
            discount_elem = element.css_first(".product-discountPercentage")
            if discount_elem:
                discount_text = discount_elem.text().strip()
                discount_match = re.search(r"(\d+)%", discount_text)
                if discount_match:
                    discount_percent = int(discount_match.group(1))

            return ProductSummary(
                id=product_id,
                name=name,
                brand=brand,
                price=Price(
                    current=current_price,
                    original=original_price,
                    currency="INR",
                    discount_percent=discount_percent,
                ),
                image_url=image_url,
                category="Fashion",
                source=self.source_name,
                url=f"{self.BASE_URL}/{href.lstrip('/')}" if href else f"{self.BASE_URL}/{product_id}",
            )

        except (AttributeError, ValueError) as e:
            if settings.debug:
                print(f"HTML parse error: {e}")
            return None

    async def get_product(self, product_id: str) -> Product | None:
        """
        Get full product details by ID.

        Args:
            product_id: Myntra product ID

        Returns:
            Full product details, or None if not found
        """
        cache_key = self._cache.cache_key("product", product_id)

        # Check cache
        cached = await self._cache.get(cache_key)
        if cached:
            return Product.model_validate(cached)

        url = f"{self.BASE_URL}/{product_id}"

        try:
            response = await self._client.get(url)
            response.raise_for_status()

            product = self._parse_product_page(response.text, product_id)

            if product:
                await self._cache.set(cache_key, product.model_dump(mode="json"))

            return product

        except httpx.HTTPError as e:
            if settings.debug:
                print(f"Product fetch error: {e}")
            return None

    def _parse_product_page(self, html: str, product_id: str) -> Product | None:
        """
        Parse full product details from product page.

        Args:
            html: Raw HTML of product page
            product_id: Product ID

        Returns:
            Full Product or None if parsing fails
        """
        # Try to extract JSON data
        data = _extract_json_object(html, "window.__myx")

        if data:
            try:
                pdp_data = data.get("pdpData", {})

                if pdp_data:
                    return self._parse_full_product_from_json(pdp_data, product_id)

            except (KeyError, TypeError):
                pass

        # Fallback: basic HTML parsing
        parser = HTMLParser(html)

        try:
            # Get basic info
            name_elem = parser.css_first("h1.pdp-title")
            brand_elem = parser.css_first("h1.pdp-name")

            name = name_elem.text().strip() if name_elem else "Unknown Product"
            brand = brand_elem.text().strip() if brand_elem else "Unknown"

            # Get price
            price_elem = parser.css_first(".pdp-price strong")
            current_price = Decimal("0")
            if price_elem:
                price_text = price_elem.text().strip()
                price_match = re.search(r"[\d,]+", price_text)
                if price_match:
                    current_price = Decimal(price_match.group().replace(",", ""))

            # Get images
            images = []
            for img in parser.css(".image-grid-image"):
                style = img.attributes.get("style", "")
                url_match = re.search(r'url\(["\']?([^"\']+)["\']?\)', style)
                if url_match:
                    img_url = url_match.group(1)
                    if not img_url.startswith("http"):
                        img_url = f"https:{img_url}"
                    images.append(ProductImage(url=img_url, alt=name))

            # Get description
            desc_elem = parser.css_first(".pdp-productDescriptorsContainer")
            description = desc_elem.text().strip() if desc_elem else ""

            # Get sizes
            sizes = []
            for size_btn in parser.css(".size-buttons-buttonContainer button"):
                size_text = size_btn.text().strip()
                if size_text:
                    sizes.append(size_text)

            return Product(
                id=product_id,
                name=name,
                brand=brand,
                price=Price(current=current_price, currency="INR"),
                image_url=images[0].url if images else f"{self.BASE_URL}/placeholder.jpg",
                category="Fashion",
                source=self.source_name,
                url=f"{self.BASE_URL}/{product_id}",
                description=description,
                images=images,
                sizes=sizes,
                colors=[],
                rating=None,
                review_count=0,
                in_stock=True,
                specifications={},
            )

        except (AttributeError, ValueError) as e:
            if settings.debug:
                print(f"Product page parse error: {e}")
            return None

    def _parse_full_product_from_json(
        self,
        data: dict,
        product_id: str,
    ) -> Product | None:
        """
        Parse full product from Myntra PDP JSON data.

        Args:
            data: PDP JSON data
            product_id: Product ID

        Returns:
            Full Product or None if parsing fails
        """
        try:
            # Get price info
            price_data = data.get("price", {})
            mrp = price_data.get("mrp", 0)
            discounted = price_data.get("discounted", mrp)
            discount = price_data.get("discount", 0)

            # Get images
            images = []
            media = data.get("media", {})
            albums = media.get("albums", [])

            for album in albums:
                for img in album.get("images", []):
                    img_url = img.get("imageURL", "")
                    if img_url:
                        if not img_url.startswith("http"):
                            img_url = f"https://assets.myntassets.com/h_720,q_90,w_540/{img_url}"
                        images.append(
                            ProductImage(
                                url=img_url,
                                alt=data.get("name", ""),
                            )
                        )

            # Get sizes
            sizes = []
            size_data = data.get("sizes", [])
            for size in size_data:
                size_label = size.get("label", "")
                if size_label and size.get("available", True):
                    sizes.append(size_label)

            # Get colors from style options
            colors = []
            style_options = data.get("styleOptions", [])
            for opt in style_options:
                color = opt.get("color", "")
                if color and color not in colors:
                    colors.append(color)

            # Get ratings
            ratings = data.get("ratings", {})
            rating = ratings.get("averageRating")
            review_count = ratings.get("totalCount", 0)

            # Get specifications
            specs = {}
            product_details = data.get("productDetails", [])
            for detail in product_details:
                title = detail.get("title", "")
                desc = detail.get("description", "")
                if title and desc:
                    specs[title] = desc

            # Check stock
            in_stock = data.get("isAvailable", True)

            # Get description
            description = data.get("productDescription", "")
            if not description:
                desc_list = data.get("articleAttributes", {})
                description = ", ".join(
                    f"{k}: {v}" for k, v in desc_list.items() if v
                )

            primary_image = ""
            if images:
                primary_image = str(images[0].url)
            elif data.get("searchImage"):
                primary_image = data["searchImage"]
                if not primary_image.startswith("http"):
                    primary_image = f"https://assets.myntassets.com/h_720,q_90,w_540/{primary_image}"

            if not primary_image:
                return None

            return Product(
                id=product_id,
                name=data.get("name", "Unknown Product"),
                brand=data.get("brand", {}).get("name", "Unknown"),
                price=Price(
                    current=Decimal(str(discounted)),
                    original=Decimal(str(mrp)) if mrp != discounted else None,
                    currency="INR",
                    discount_percent=int(discount) if discount else None,
                ),
                image_url=primary_image,
                category=data.get("articleType", {}).get("typeName", "Fashion"),
                source=self.source_name,
                url=f"{self.BASE_URL}/{product_id}",
                description=description,
                images=images,
                sizes=sizes,
                colors=colors,
                rating=float(rating) if rating else None,
                review_count=review_count,
                in_stock=in_stock,
                specifications=specs,
            )

        except (KeyError, ValueError, TypeError) as e:
            if settings.debug:
                print(f"Full product parse error: {e}")
            return None

    async def get_trending(
        self,
        category: str | None = None,
        limit: int = 20,
    ) -> list[ProductSummary]:
        """
        Get trending/popular products.

        Uses Myntra's trending/popular section.

        Args:
            category: Optional category filter
            limit: Max results to return

        Returns:
            List of trending products
        """
        cache_key = self._cache.cache_key("trending", category or "all")

        # Check cache
        cached = await self._cache.get(cache_key)
        if cached:
            products = [ProductSummary.model_validate(p) for p in cached]
            return products[:limit]

        # Build URL for trending page
        if category:
            url = f"{self.BASE_URL}/{category.lower().replace(' ', '-')}?sort=popularity"
        else:
            url = f"{self.BASE_URL}/clothing?sort=popularity"

        try:
            response = await self._client.get(url)
            response.raise_for_status()

            products = self._parse_search_results(response.text, limit)

            # Cache results
            await self._cache.set(
                cache_key,
                [p.model_dump(mode="json") for p in products],
            )

            return products

        except httpx.HTTPError as e:
            if settings.debug:
                print(f"Trending fetch error: {e}")
            return []

    async def close(self) -> None:
        """Clean up HTTP client."""
        await self._client.aclose()

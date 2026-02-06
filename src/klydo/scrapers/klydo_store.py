"""
Klydo brand scraper.

Uses the public klydo.in catalog API to fetch products.
"""

from __future__ import annotations

import time
from decimal import Decimal
from typing import Any

import httpx

from klydo.config import settings
from klydo.logging import logger, log_cache_hit, log_cache_miss, log_api_call, log_api_error
from klydo.models.product import Price, Product, ProductImage, ProductSummary
from klydo.scrapers.cache import Cache


class KlydoStoreScraper:
    """Scraper for klydo.in."""

    BASE_URL = "https://api.klydo.in"
    WEB_BASE_URL = "https://www.klydo.in"

    def __init__(self) -> None:
        self._session_id = settings.klydo_session_id or self._generate_session_id()
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=self._get_headers(),
            timeout=settings.request_timeout,
            follow_redirects=True,
        )
        self._cache = Cache(namespace="klydo-store", default_ttl=settings.cache_ttl)
        logger.debug(f"KlydoStoreScraper initialized | session_id={self._session_id}")

    @property
    def source_name(self) -> str:
        """Human-readable source name."""
        return "Klydo"

    def _generate_session_id(self) -> str:
        now_ms = int(time.time() * 1000)
        suffix = int(time.time_ns() % 1_000_000)
        return f"{now_ms}-{suffix}"

    def _get_headers(self) -> dict[str, str]:
        # Token must be provided via KLYDO_KLYDO_API_TOKEN environment variable
        token = settings.klydo_api_token

        headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,kn;q=0.7",
            "authorization": f"Bearer {token}" if token else "",
            "content-type": "application/json",
            "dnt": "1",
            "origin": self.WEB_BASE_URL,
            "priority": "u=1, i",
            "referer": f"{self.WEB_BASE_URL}/",
            "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": (
                "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/143.0.0.0 Mobile Safari/537.36"
            ),
            "x-app-buildnumber": "63",
            "x-app-name": "Customer",
            "x-app-platform": "Web",
            "x-session-id": self._session_id,
        }

        # Drop empty auth header if token was not provided
        return {k: v for k, v in headers.items() if v}

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
        cache_key = self._cache.cache_key(
            "search",
            query,
            category or "",
            gender or "",
            str(min_price or ""),
            str(max_price or ""),
            str(limit),
        )

        if cached := await self._cache.get(cache_key):
            log_cache_hit(cache_key)
            products = [ProductSummary.model_validate(item) for item in cached][:limit]
            await self._warm_summary_cache(products)
            return products

        log_cache_miss(cache_key)

        params: dict[str, Any] = {
            "query": query,
            "limit": min(limit, 50),
            "includeFilters": "true",
        }

        if gender:
            params["audience"] = gender.lower()
        if category:
            params["query"] = f"{query} {category}"

        try:
            log_api_call(self.source_name, "/catalog/search")
            response = await self._client.get("/catalog/search", params=params)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            log_api_error(
                self.source_name,
                "/catalog/search",
                str(exc),
                status_code=getattr(exc.response, "status_code", None) if hasattr(exc, "response") else None,
            )
            return []

        products: list[ProductSummary] = []
        for item in data.get("products", [])[:limit]:
            product = self._parse_product_summary(item)
            if not product:
                continue
            # Apply price filters in rupees
            if min_price is not None and product.price.current < min_price:
                continue
            if max_price is not None and product.price.current > max_price:
                continue
            products.append(product)

        if products:
            await self._cache.set(
                cache_key,
                [p.model_dump(mode="json") for p in products],
            )
            await self._warm_summary_cache(products)

        logger.debug(f"Klydo search complete | query={query} | results={len(products)}")
        return products

    async def _warm_summary_cache(self, products: list[ProductSummary]) -> None:
        """Store summaries keyed by styleId for PDP fallback."""
        for product in products:
            try:
                await self._cache.set(
                    self._cache.cache_key("summary", product.id),
                    product.model_dump(mode="json"),
                )
            except Exception as e:
                logger.debug(f"Summary cache warm failed for {product.id}: {e}")

    def _parse_product_summary(self, item: dict[str, Any]) -> ProductSummary | None:
        style_id = item.get("styleId")
        image_url = item.get("imageUrl")
        name = item.get("title") or "Unknown Product"
        brand = item.get("brand") or "Klydo"

        if not style_id or not image_url:
            return None

        selling_price = self._to_rupees(item.get("sellingPrice"))
        mrp_value = self._to_rupees(item.get("mrp"))
        discount_percent = self._discount_percent(
            selling_price, mrp_value, item.get("discountPercentage")
        )

        original_price = mrp_value if mrp_value and mrp_value > 0 else None
        category_value = item.get("category") or "Fashion"

        return ProductSummary(
            id=str(style_id),
            name=name,
            brand=brand,
            price=Price(
                current=selling_price,
                original=original_price,
                currency="INR",
                discount_percent=discount_percent,
            ),
            image_url=image_url,
            category=category_value,
            source=self.source_name,
            url=self._build_product_url(style_id, item.get("slug")),
        )

    async def get_product(self, product_id: str) -> Product | None:
        cache_key = self._cache.cache_key("product", product_id)
        if cached := await self._cache.get(cache_key):
            log_cache_hit(cache_key)
            return Product.model_validate(cached)

        log_cache_miss(cache_key)
        is_sku = product_id.startswith("SKU_")

        # If we already cached a summary from a previous search, keep it for fallback
        summary_cache_key = self._cache.cache_key("summary", product_id)
        cached_summary = await self._cache.get(summary_cache_key)
        summary_from_cache = (
            ProductSummary.model_validate(cached_summary) if cached_summary else None
        )

        detail = await self._fetch_product_detail(product_id, is_sku=is_sku)
        product = None

        if detail:
            product = self._parse_product_detail(
                detail,
                product_id,
                target_sku=product_id if is_sku else None,
            )

        if not product:
            # Fallback to summary-only product from cache
            if summary_from_cache:
                logger.debug(f"Using cached summary fallback for {product_id}")
                product = self._product_from_summary(summary_from_cache)

        if not product:
            # As a last resort, try a search using the ID as query
            logger.debug(f"Attempting search fallback for {product_id}")
            summaries = await self.search(query=product_id, limit=10)
            summary = next((s for s in summaries if s.id == product_id), None)
            if summary:
                product = self._product_from_summary(summary)

        if product:
            await self._cache.set(cache_key, product.model_dump(mode="json"))

        return product

    async def _fetch_product_detail(
        self, identifier: str, is_sku: bool = False
    ) -> dict[str, Any] | None:
        """
        Try a handful of likely PDP endpoints.
        """
        if is_sku:
            endpoints = [
                (f"/catalog/product/{identifier}", None),
                ("/catalog/product", {"skuId": identifier}),
                ("/catalog/pdp", {"skuId": identifier}),
            ]
        else:
            endpoints = [
                ("/catalog/pdp", {"styleId": identifier}),
                ("/catalog/product", {"styleId": identifier}),
                (f"/catalog/products/{identifier}", None),
                (f"/catalog/styles/{identifier}", None),
            ]

        for path, params in endpoints:
            try:
                log_api_call(self.source_name, path)
                response = await self._client.get(path, params=params)
                response.raise_for_status()
                data = response.json()
                if data:
                    return data
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code in (400, 404):
                    continue
                log_api_error(
                    self.source_name,
                    path,
                    str(exc),
                    status_code=exc.response.status_code,
                )
            except Exception as exc:  # noqa: BLE001
                log_api_error(self.source_name, path, str(exc))
        return None

    def _parse_product_detail(
        self,
        data: dict[str, Any],
        requested_style_id: str,
        target_sku: str | None = None,
    ) -> Product | None:
        styles = data.get("styles") or []
        if not styles and data.get("styleId"):
            styles = [data]

        style = next(
            (s for s in styles if s.get("styleId") == requested_style_id),
            styles[0] if styles else None,
        )

        if target_sku:
            for candidate in styles:
                for sz in candidate.get("sizes", []):
                    if sz.get("skuId") == target_sku:
                        style = candidate
                        break
                if style == candidate:
                    break

        if not style:
            return None

        title = style.get("title") or data.get("title") or "Unknown Product"
        brand = data.get("brandName") or style.get("brand") or "Klydo"
        slug = style.get("slug") or requested_style_id

        images = []
        for media in style.get("media", []):
            url = media.get("url")
            if url:
                images.append(ProductImage(url=url, alt=title))

        # Choose price from selected SKU or first available size
        sizes_data = style.get("sizes", [])
        selected_sku = target_sku or data.get("selectedSkuId")
        size_entry = next(
            (s for s in sizes_data if s.get("skuId") == selected_sku),
            None,
        )
        if not size_entry:
            size_entry = next(
                (s for s in sizes_data if s.get("inventory", {}).get("available")),
                sizes_data[0] if sizes_data else None,
            )

        price = self._price_from_size(size_entry)

        description = style.get("description", "") or ""
        if not description and style.get("specifications"):
            description = "; ".join(
                f"{spec.get('name')}: {spec.get('value')}"
                for spec in style["specifications"]
                if spec.get("name") and spec.get("value")
            )

        primary_image = images[0].url if images else None
        if not primary_image:
            fallback = style.get("imageUrl") or data.get("imageUrl")
            if fallback:
                primary_image = fallback

        if not primary_image:
            return None

        sizes = [
            s.get("size")
            for s in sizes_data
            if s.get("size") and s.get("inventory", {}).get("available", True)
        ]

        specifications = {
            spec.get("name"): spec.get("value")
            for spec in style.get("specifications", [])
            if spec.get("name") and spec.get("value")
        }

        in_stock = (
            any(s.get("inventory", {}).get("available") for s in sizes_data)
            if sizes_data
            else True
        )

        colors = []
        label = style.get("label")
        if label:
            colors.append(label)

        return Product(
            id=str(style.get("styleId", requested_style_id)),
            name=title,
            brand=brand,
            price=price,
            image_url=primary_image,
            category="Fashion",
            source=self.source_name,
            url=self._build_product_url(requested_style_id, slug),
            description=description,
            images=images or [ProductImage(url=primary_image, alt=title)],
            sizes=sizes,
            colors=colors,
            rating=None,
            review_count=0,
            in_stock=in_stock,
            specifications=specifications,
        )

    def _product_from_summary(self, summary: ProductSummary) -> Product:
        """Convert a ProductSummary into a minimal Product payload."""
        return Product(
            id=summary.id,
            name=summary.name,
            brand=summary.brand,
            price=summary.price,
            image_url=summary.image_url,
            category=summary.category,
            source=summary.source,
            url=summary.url,
            description="",
            images=[ProductImage(url=summary.image_url, alt=summary.name)],
            sizes=[],
            colors=[],
            rating=None,
            review_count=0,
            in_stock=True,
            specifications={},
        )

    def _build_product_url(self, style_id: str, slug: str | None) -> str:
        if slug:
            return f"{self.WEB_BASE_URL}/p/{slug}"
        return f"{self.WEB_BASE_URL}/style/{style_id}"

    def _discount_percent(
        self, selling_price: Decimal, mrp: Decimal, provided_discount: int | None
    ) -> int | None:
        if provided_discount is not None:
            try:
                return int(provided_discount)
            except (TypeError, ValueError):
                pass
        if mrp and mrp > selling_price and selling_price > 0:
            return int(((mrp - selling_price) / mrp) * 100)
        return None

    def _price_from_size(self, size_entry: dict[str, Any] | None) -> Price:
        if not size_entry:
            return Price(current=Decimal("0"), currency="INR")

        selling_price = self._to_rupees(size_entry.get("sellingPrice"))
        mrp_value = self._to_rupees(size_entry.get("mrp"))
        discount_percent = self._discount_percent(
            selling_price, mrp_value, size_entry.get("discountPercentage")
        )

        return Price(
            current=selling_price,
            original=mrp_value if mrp_value and mrp_value > 0 else None,
            currency="INR",
            discount_percent=discount_percent,
        )

    def _to_rupees(self, value: Any) -> Decimal:
        try:
            return Decimal(str(value)) / Decimal("100")
        except (TypeError, ValueError, ArithmeticError):
            return Decimal("0")

    async def get_trending(
        self,
        category: str | None = None,
        limit: int = 20,
    ) -> list[ProductSummary]:
        # The API does not expose a dedicated trending endpoint publicly;
        # reuse search with a sensible default query.
        query = category or "T-Shirts"
        logger.debug(f"Klydo get_trending | query={query} | limit={limit}")
        return await self.search(query=query, limit=limit)

    async def close(self) -> None:
        logger.debug("Closing KlydoStoreScraper")
        await self._client.aclose()
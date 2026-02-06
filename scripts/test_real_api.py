#!/usr/bin/env python
"""
Real API test for Klydo MCP Server.

This script tests the actual Klydo.in API to verify the scraper works correctly.
"""

import asyncio
from dotenv import load_dotenv
load_dotenv()  # Load environment variables before importing klydo modules

from klydo.scrapers.klydo_store import KlydoStoreScraper


async def test_real_api():
    print("=" * 60)
    print("           KLYDO MCP SERVER - REAL API TEST")
    print("=" * 60)
    print()

    scraper = KlydoStoreScraper()

    # Test 1: Search products
    print("1. Testing search_products (query='t-shirt', limit=3)...")
    print("-" * 40)
    try:
        results = await scraper.search("t-shirt", limit=3)
        print(f"   ✅ Found {len(results)} products")
        for i, p in enumerate(results[:3], 1):
            print(f"\n   Product {i}:")
            print(f"   Brand: {p.brand}")
            print(f"   Name: {p.name}")
            print(f"   Price: ₹{p.price.current} (Original: ₹{p.price.original})")
            print(f"   URL: {p.url}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print()

    # Test 2: Get trending
    print("\n2. Testing get_trending (limit=3)...")
    print("-" * 40)
    try:
        trending = await scraper.get_trending(limit=3)
        print(f"   ✅ Found {len(trending)} trending products")
        for i, p in enumerate(trending[:3], 1):
            print(f"\n   Trending {i}:")
            print(f"   Brand: {p.brand}")
            print(f"   Name: {p.name}")
            print(f"   Price: ₹{p.price.current}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print()

    # Test 3: Get product details
    if results:
        print(f"\n3. Testing get_product_details (id={results[0].id})...")
        print("-" * 40)
        try:
            product = await scraper.get_product(results[0].id)
            if product:
                print("   ✅ Got product details")
                print(f"   Name: {product.name}")
                print(f"   Brand: {product.brand}")
                desc = product.description[:100] + "..." if len(product.description) > 100 else product.description
                print(f"   Description: {desc}")
                print(f"   Sizes: {product.sizes}")
                print(f"   Colors: {product.colors}")
                print(f"   Images: {len(product.images)} images")
                print(f"   Rating: {product.rating} ({product.review_count} reviews)")
                print(f"   In Stock: {product.in_stock}")
            else:
                print("   ⚠️ No details returned (product might need authentication)")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()

    await scraper.close()
    print()
    print("=" * 60)
    print("                    TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_real_api())
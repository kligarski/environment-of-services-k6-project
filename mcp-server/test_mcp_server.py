import asyncio
import os

from main import mcp


async def test_tools():
    print("Testing list_products...")
    products = await mcp.call_tool("list_products", arguments={"query": "Laptop"})
    print(f"Result: {products}")

    print("\nTesting get_shipping_quote...")
    # Using IDs that should exist (1 is usually first in seeded data)
    shipping = await mcp.call_tool(
        "get_shipping_quote", arguments={"items": [{"id": 1, "count": 1}]}
    )
    print(f"Result: {shipping}")

    print("\nTesting optimize_packaging...")
    packaging = await mcp.call_tool(
        "optimize_packaging",
        arguments={"items": [{"id": 1, "count": 5}, {"id": 2, "count": 2}]},
    )
    print(f"Result: {packaging}")


if __name__ == "__main__":
    asyncio.run(test_tools())

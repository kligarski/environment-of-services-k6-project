import os
from typing import List, Optional

import httpx
from fastmcp import FastMCP
from pydantic import BaseModel

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

mcp = FastMCP("Logistics Assistant")


@mcp.tool()
async def list_products(query: Optional[str] = None) -> str:
    """
    List available products from the catalog.
    Optional query parameter to filter products by name.
    """
    async with httpx.AsyncClient() as client:
        params = {"query": query} if query else {}
        response = await client.get(f"{BACKEND_URL}/products", params=params)
        response.raise_for_status()
        products = response.json()

        if not products:
            return "No products found."

        result = "Available Products:\n"
        for p in products:
            result += f"- ID {p['id']}: {p['name']} (${p['price']}) - {p['weight']}g, {p['dim_x']}x{p['dim_y']}x{p['dim_z']}cm\n"
        return result


@mcp.tool()
async def get_shipping_quote(items: List[dict]) -> str:
    """
    Get shipping quotes for a list of items.
    'items' should be a list of dicts with 'id' (int) and 'count' (int).
    Example: [{"id": 1, "count": 2}, {"id": 5, "count": 1}]
    """
    async with httpx.AsyncClient() as client:
        payload = {"products": items}
        response = await client.post(f"{BACKEND_URL}/shipping/quote", json=payload)

        if response.status_code == 404:
            return "Error: One or more products not found."
        response.raise_for_status()
        data = response.json()

        quotes = data.get("quotes", [])
        if not quotes:
            return "No shipping quotes available."

        result = "Shipping Quotes:\n"
        for q in quotes:
            price_str = f"${q['price']:.2f}" if q["price"] is not None else "N/A"
            result += f"- {q['provider']}: {price_str}, Estimated Days: {q['estimated_days']}\n"
        return result


@mcp.tool()
async def optimize_packaging(items: List[dict]) -> str:
    """
    Calculate optimal packaging for a list of items.
    'items' should be a list of dicts with 'id' (int) and 'count' (int).
    Example: [{"id": 1, "count": 10}, {"id": 2, "count": 5}]
    """
    async with httpx.AsyncClient() as client:
        payload = {"items": items}
        response = await client.post(f"{BACKEND_URL}/packaging/optimize", json=payload)

        if response.status_code == 404:
            return "Error: One or more products not found."
        response.raise_for_status()
        data = response.json()

        result = f"Packaging Optimization Result:\n"
        result += f"Total Weight: {data['total_weight_g']:.2f}g, Total Volume: {data['total_volume_cm3']:.2f}cm3\n\n"

        for i, box in enumerate(data.get("boxes", []), 1):
            result += f"Box {i} ({box['box_type']}):\n"
            result += f"  Weight: {box['total_weight_g']:.2f}g, Volume: {box['total_volume_cm3']:.2f}cm3\n"
            result += "  Items:\n"
            for item in box["items"]:
                result += f"    - Product ID {item['id']}: Count {item['count']}\n"
        return result


if __name__ == "__main__":
    mcp.run()

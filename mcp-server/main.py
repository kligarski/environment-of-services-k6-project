import os
from typing import List, Optional

import httpx
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from telemetry import setup_telemetry

setup_telemetry()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

mcp = FastMCP(
    "Logistics Assistant",
    instructions="A specialized assistant for managing product catalogs, calculating shipping costs, and optimizing warehouse packaging.",
)


class ShipmentItem(BaseModel):
    id: int = Field(..., description="Product ID from catalog")
    count: int = Field(..., ge=1, description="Quantity of products")


@mcp.tool()
async def list_products(query: Optional[str] = None) -> str:
    """
    Search and list products from the logistics catalog.

    Use this tool to find product IDs, prices, and dimensions.

    Args:
        query: Optional search term to filter products by name (e.g., 'laptop', 'chair').
    """
    async with httpx.AsyncClient() as client:
        params = {"query": query} if query else {}
        response = await client.get(f"{BACKEND_URL}/products", params=params)
        response.raise_for_status()
        products = response.json()

        if not products:
            return "No products found matching the criteria."

        result = "Catalog Products:\n"
        for p in products:
            result += f"- [ID {p['id']}] {p['name']}: ${p['price']} | Weight: {p['weight']}g | Dims: {p['dim_x']}x{p['dim_y']}x{p['dim_z']}cm\n"
        return result


@mcp.tool()
async def get_shipping_quote(items: List[ShipmentItem]) -> str:
    """
    Request shipping price estimates and delivery times from multiple providers.

    Args:
        items: A list of products to ship. Each item MUST be a dictionary with:
               - 'id': The integer ID of the product from the catalog.
               - 'count': The quantity of this product (integer).
               Example: [{"id": 1, "count": 2}, {"id": 10, "count": 1}]
    """
    async with httpx.AsyncClient() as client:
        payload = {"products": [item.model_dump() for item in items]}
        response = await client.post(f"{BACKEND_URL}/shipping/quote", json=payload)

        if response.status_code == 404:
            return "Error: One or more Product IDs were not found in the catalog. Please verify IDs using list_products."
        response.raise_for_status()
        data = response.json()

        quotes = data.get("quotes", [])
        if not quotes:
            return "No shipping quotes could be generated for the selected items."

        result = "Available Shipping Quotes:\n"
        for q in quotes:
            price_str = (
                f"${q['price']:.2f}" if q["price"] is not None else "Quote Unavailable"
            )
            result += f"- Provider: {q['provider']} | Cost: {price_str} | Estimated Delivery: {q['estimated_days']}\n"
        return result


@mcp.tool()
async def optimize_packaging(items: List[ShipmentItem]) -> str:
    """
    Calculate the most efficient way to pack multiple items into shipping boxes.

    This tool uses a 3D bin-packing algorithm to minimize empty space and provide a manifest.

    Args:
        items: A list of products to pack. Each item MUST be a dictionary with:
               - 'id': The integer ID of the product.
               - 'count': The quantity to pack.
               Example: [{"id": 5, "count": 10}]
    """
    async with httpx.AsyncClient() as client:
        payload = {"items": [item.model_dump() for item in items]}
        response = await client.post(f"{BACKEND_URL}/packaging/optimize", json=payload)

        if response.status_code == 404:
            return "Error: Product IDs not found. Ensure you are using valid IDs from the catalog."
        response.raise_for_status()
        data = response.json()

        result = "Packaging Optimization Strategy:\n"
        result += f"Summary: Total Weight {data['total_weight_g']:.2f}g | Total Volume {data['total_volume_cm3']:.2f}cm3\n\n"

        for i, box in enumerate(data.get("boxes", []), 1):
            result += f"Container {i} [{box['box_type']}]:\n"
            result += f"  - Stats: {box['total_weight_g']:.2f}g, {box['total_volume_cm3']:.2f}cm3\n"
            result += "  - Contents:\n"
            for item in box["items"]:
                result += f"    • Product ID {item['id']}: {item['count']} unit(s)\n"
        return result


@mcp.prompt()
def logistics_workflow() -> str:
    """Guidelines for the Logistics Assistant."""
    return """You are a Logistics Expert. To help the user effectively:
1. ALWAYS start by searching for products using 'list_products' if the user provides names instead of IDs.
2. When the user wants to send items, use 'get_shipping_quote' to compare providers.
3. For large orders or warehouse inquiries, use 'optimize_packaging' to suggest the best container configuration.
4. Be precise with Product IDs and counts."""


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8080, stateless_http=True)

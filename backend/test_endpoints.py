import os
import sys

from fastapi.testclient import TestClient

# Add current directory to path so we can import backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_products():
    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_shipping_quote():
    # Get a product first to have a valid ID
    products = client.get("/products").json()
    if not products:
        print("No products found, cannot test shipping quote")
        return

    product_id = products[0]["id"]
    payload = {"products": [{"id": product_id, "count": 2}]}

    response = client.post("/shipping/quote", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "quotes" in data
    assert len(data["quotes"]) == 4

    # Check if we have quotes for expected providers
    providers = [q["provider"] for q in data["quotes"]]
    assert "OutPost" in providers
    assert "SPU" in providers

    print("Shipping quote test data:", data)


def test_shipping_quote_invalid_product():
    payload = {"products": [{"id": 999999, "count": 1}]}
    response = client.post("/shipping/quote", json=payload)
    assert response.status_code == 404


if __name__ == "__main__":
    try:
        print("Running health check test...")
        test_health()
        print("Running products test...")
        test_products()
        print("Running shipping quote test...")
        test_shipping_quote()
        print("Running invalid product test...")
        test_shipping_quote_invalid_product()
        print("\nAll tests passed successfully!")
    except Exception as e:
        print(f"\nTests failed: {e}")
        sys.exit(1)

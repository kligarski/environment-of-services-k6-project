import asyncio
import hashlib
import random
import time
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from . import schemas
from .database import Product, SessionLocal, init_db, seed_data

app = FastAPI(title="Logistics Assistant Backend")


async def simulate_provider_delay(provider_name: str):
    # Base delays and multipliers for providers
    config = {
        "OutPost": {"base": 0.1, "mult": 1.0},
        "LHD": {"base": 0.2, "mult": 1.2},
        "SPU": {"base": 0.3, "mult": 1.5},
        "PDP": {"base": 0.15, "mult": 1.1},
    }

    c = config.get(provider_name, {"base": 0.2, "mult": 1.0})
    # Random jitter: 80% to 120% of base delay
    delay = c["base"] * c["mult"] * (0.8 + random.random() * 0.4)

    # 5% chance of a significant delay (network spike simulation)
    if random.random() < 0.05:
        delay += random.uniform(1.0, 2.5)

    await asyncio.sleep(delay)


async def get_quote_for_provider(provider: str, weight_g: float, volume: float):
    await simulate_provider_delay(provider)

    # Provider-specific logic (converts weight to kg for pricing)
    weight_kg = weight_g / 1000.0

    if provider == "OutPost":
        # OutPost has strict limits for package lockers
        if weight_kg > 25 or volume > 100000:  # Max 25kg or approx 100L
            return None, "1 day"
        return 15.0 + 1.0 * weight_kg, "1 day"

    elif provider == "LHD":
        if weight_kg > 300:
            return None, "2-3 days"
        return 20.0 + 2.0 * weight_kg, "2-3 days"

    elif provider == "SPU":
        if weight_kg > 20:
            return None, "3-7 days"
        return 10.0 + 0.5 * weight_kg, "3-7 days"

    elif provider == "PDP":
        # PDP handles the heaviest loads
        if weight_kg > 500:
            return None, "1-2 days"
        return 25.0 + 1.5 * weight_kg, "1-2 days"

    return None, "Unknown"


# Initialize database and seed data on startup
@app.on_event("startup")
def startup_event():
    init_db()
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/products", response_model=List[schemas.Product])
def get_products(query: Optional[str] = Query(None), db: Session = Depends(get_db)):
    products_query = db.query(Product)
    if query:
        products_query = products_query.filter(Product.name.ilike(f"%{query}%"))
    return products_query.all()


@app.post("/shipping/quote", response_model=schemas.ShippingQuoteResponse)
async def get_shipping_quotes(
    request: schemas.ShippingQuoteRequest, db: Session = Depends(get_db)
):
    product_ids = [p.id for p in request.products]
    db_products = {
        p.id: p for p in db.query(Product).filter(Product.id.in_(product_ids)).all()
    }

    if not db_products:
        raise HTTPException(status_code=404, detail="No products found for given IDs")

    total_weight = 0.0
    total_volume = 0.0

    for item in request.products:
        product = db_products.get(item.id)
        if product:
            total_weight += product.weight * item.count
            total_volume += (product.dim_x * product.dim_y * product.dim_z) * item.count

    providers = ["OutPost", "LHD", "SPU", "PDP"]

    # Run all provider simulations concurrently
    tasks = [get_quote_for_provider(p, total_weight, total_volume) for p in providers]
    results = await asyncio.gather(*tasks)

    quotes = []
    for provider, (price, days) in zip(providers, results):
        quotes.append(
            schemas.ShippingProviderQuote(
                provider=provider, price=price, estimated_days=days
            )
        )

    return schemas.ShippingQuoteResponse(quotes=quotes)


def simulate_cpu_load(item_count: int):
    """
    Simulates a CPU-bound task by performing redundant calculations.
    Growth is exponential: complexity ~ O(1.5^n) to simulate heavy algorithms.
    """
    # Exponential scaling: 50k * (1.5 ^ item_count)
    # 1 item: 75k iterations (~ms)
    # 10 items: ~2.8M iterations (~0.5-1s)
    # 20 items: ~166M iterations (several seconds)
    base_iterations = 50_000
    iterations = int(base_iterations * (1.5 ** min(item_count, 25)))

    result = 0
    for i in range(iterations):
        result += (i * i) % 123
        if i % 1000 == 0:
            hashlib.sha256(str(i).encode()).hexdigest()
    return result


@app.post("/packaging/optimize", response_model=schemas.PackagingResponse)
async def optimize_packaging(
    request: schemas.PackagingRequest, db: Session = Depends(get_db)
):
    product_ids = [p.id for p in request.items]
    db_products = {
        p.id: p for p in db.query(Product).filter(Product.id.in_(product_ids)).all()
    }

    if not db_products:
        raise HTTPException(status_code=404, detail="No products found for given IDs")

    total_weight = 0.0
    total_volume = 0.0
    total_items_count = sum(p.count for p in request.items)

    # 1. Simulating heavy CPU-bound optimization logic
    # This call is synchronous and DELIBERATELY blocks the FastAPI event loop
    simulate_cpu_load(total_items_count)

    # 2. Simple Heuristic: Pack into boxes based on total volume
    # Max volume per standard box is 50,000 cm3
    BOX_CAPACITY = 50000.0

    for item in request.items:
        product = db_products.get(item.id)
        if product:
            total_weight += product.weight * item.count
            total_volume += (product.dim_x * product.dim_y * product.dim_z) * item.count

    # Distribute into boxes (very simple logic)
    num_boxes = int(total_volume // BOX_CAPACITY) + 1
    boxes = []

    # Simple distribution of items across boxes (just for show)
    for i in range(num_boxes):
        box_items = []
        # In this simple heuristic, we just partition the requested items
        # proportionally across boxes for the response structure
        for item in request.items:
            count_in_box = item.count // num_boxes
            if i == num_boxes - 1:  # Last box gets the remainder
                count_in_box += item.count % num_boxes

            if count_in_box > 0:
                box_items.append(schemas.ProductItem(id=item.id, count=count_in_box))

        boxes.append(
            schemas.PackagingBox(
                box_type="EcoBox-Standard" if total_volume < 100000 else "MaxiPallet",
                items=box_items,
                total_weight_g=total_weight / num_boxes,
                total_volume_cm3=total_volume / num_boxes,
            )
        )

    return schemas.PackagingResponse(
        boxes=boxes, total_volume_cm3=total_volume, total_weight_g=total_weight
    )

import asyncio
import random
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


async def get_quote_for_provider(provider: str, weight: float, volume: float):
    await simulate_provider_delay(provider)

    # Provider-specific logic
    if provider == "OutPost":
        # OutPost has strict limits for package lockers
        if weight > 25 or volume > 100000:  # Max 25kg or approx 100L
            return None, "1 day"
        return 15.0 + 1.0 * weight, "1 day"

    elif provider == "LHD":
        if weight > 300:
            return None, "2-3 days"
        return 20.0 + 2.0 * weight, "2-3 days"

    elif provider == "SPU":
        if weight > 20:
            return None, "3-7 days"
        return 10.0 + 0.5 * weight, "3-7 days"

    elif provider == "PDP":
        # PDP handles the heaviest loads
        if weight > 500:
            return None, "1-2 days"
        return 25.0 + 1.5 * weight, "1-2 days"

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

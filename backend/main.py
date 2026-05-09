import asyncio
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from . import packaging_logic, schemas, shipping_logic
from .database import Product, SessionLocal, init_db, seed_data

app = FastAPI(title="Logistics Assistant Backend")


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
    tasks = [
        shipping_logic.get_quote_for_provider(p, total_weight, total_volume)
        for p in providers
    ]
    results = await asyncio.gather(*tasks)

    quotes = []
    for provider, (price, days) in zip(providers, results):
        quotes.append(
            schemas.ShippingProviderQuote(
                provider=provider, price=price, estimated_days=days
            )
        )

    return schemas.ShippingQuoteResponse(quotes=quotes)


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

    return packaging_logic.optimize_packaging_logic(request.items, db_products)

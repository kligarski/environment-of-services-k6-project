from typing import List, Optional

from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session

from . import schemas
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

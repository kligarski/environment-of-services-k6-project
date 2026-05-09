from typing import List, Optional

from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    price: float
    weight: float
    dim_x: float
    dim_y: float
    dim_z: float


class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True

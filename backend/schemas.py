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
        from_attributes = True


class ProductItem(BaseModel):
    id: int
    count: int


class ShippingQuoteRequest(BaseModel):
    products: List[ProductItem]


class ShippingProviderQuote(BaseModel):
    provider: str
    price: Optional[float]
    estimated_days: str


class ShippingQuoteResponse(BaseModel):
    quotes: List[ShippingProviderQuote]


class PackagingRequest(BaseModel):
    items: List[ProductItem]


class PackagingBox(BaseModel):
    box_type: str
    items: List[ProductItem]
    total_weight_g: float
    total_volume_cm3: float


class PackagingResponse(BaseModel):
    boxes: List[PackagingBox]
    total_volume_cm3: float
    total_weight_g: float

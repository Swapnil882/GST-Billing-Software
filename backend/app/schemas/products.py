from typing import Optional
from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    kind: Optional[str] = "goods"  # goods or service
    price: float = 0.0
    hsn: Optional[str] = ""
    sac: Optional[str] = ""
    gst: Optional[float] = 18.0
    unit: Optional[str] = "NOS"
    stock: Optional[float] = None
    purchasePrice: Optional[float] = None
    lowStockThreshold: Optional[float] = None

class ProductCreate(ProductBase):
    id: Optional[str] = None

class ProductResponse(ProductBase):
    id: str

from typing import Optional, Any
from pydantic import BaseModel

class PurchasePayment(BaseModel):
    id: Optional[str] = None
    amount: float
    date: str
    mode: Optional[str] = "other"
    reference: Optional[str] = ""
    note: Optional[str] = ""

class PurchaseCreate(BaseModel):
    id: Optional[str] = None
    supplierName: str
    date: str
    totalAmount: float
    tdsAmount: Optional[float] = 0.0
    invoiceNumber: Optional[str] = ""
    payments: Optional[list[PurchasePayment]] = None
    items: Optional[list[dict[str, Any]]] = None

class PurchaseOrderCreate(BaseModel):
    id: Optional[str] = None
    poNumber: str
    supplierName: str
    date: str
    totalAmount: float
    items: Optional[list[dict[str, Any]]] = None
    status: Optional[str] = "open"

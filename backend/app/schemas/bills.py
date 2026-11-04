from typing import Optional, Any
from pydantic import BaseModel, Field

class BillItem(BaseModel):
    name: str
    description: Optional[str] = ""
    rate: float = 0.0
    qty: float = 1.0
    unit: Optional[str] = "NOS"
    gst: Optional[float] = 18.0
    hsn: Optional[str] = ""
    discount: Optional[float] = 0.0
    discountType: Optional[str] = "rupee"
    cess: Optional[float] = 0.0

class BillPayment(BaseModel):
    id: Optional[str] = None
    amount: float
    date: str
    mode: str = "other"
    reference: Optional[str] = ""
    note: Optional[str] = ""
    creditSourceBillIds: Optional[list[str]] = None

class BillCreate(BaseModel):
    id: str
    invoiceNumber: str
    invoiceDate: str
    clientName: str
    invoiceType: Optional[str] = "tax-invoice"
    currency: Optional[str] = "INR"
    totalAmount: float
    totalTaxAmount: Optional[float] = 0.0
    status: Optional[str] = "unpaid"
    paidAmount: Optional[float] = 0.0
    payments: Optional[list[BillPayment]] = []
    data: Optional[dict[str, Any]] = None

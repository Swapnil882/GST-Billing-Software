from typing import Optional, Any
from pydantic import BaseModel

class RecurringTemplateCreate(BaseModel):
    id: Optional[str] = None
    clientName: str
    frequency: str = "monthly"  # weekly, monthly, quarterly, yearly
    interval: Optional[int] = 1
    nextDate: str
    totalAmount: float
    totalTaxAmount: Optional[float] = 0.0
    active: Optional[bool] = True
    endMode: Optional[str] = "never"  # never, onDate, afterN
    endDate: Optional[str] = None
    maxOccurrences: Optional[int] = None
    occurrencesCreated: Optional[int] = 0
    invoiceType: Optional[str] = "tax-invoice"
    items: Optional[list[dict[str, Any]]] = None
    invoiceOptions: Optional[dict[str, Any]]] = None

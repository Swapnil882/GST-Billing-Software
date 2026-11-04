from typing import Optional
from pydantic import BaseModel

class CashEntryCreate(BaseModel):
    id: Optional[str] = None
    type: str  # 'in' or 'out'
    date: str
    amount: float
    name: Optional[str] = ""
    note: Optional[str] = ""
    category: Optional[str] = ""
    ownerGstin: Optional[str] = ""
    ownerName: Optional[str] = ""

class CashEntryResponse(CashEntryCreate):
    id: str
    createdAt: Optional[str] = None

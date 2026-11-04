from typing import Optional, Any
from pydantic import BaseModel

class BusinessProfile(BaseModel):
    id: Optional[str] = None
    businessName: Optional[str] = ""
    address: Optional[str] = ""
    state: Optional[str] = ""
    gstin: Optional[str] = ""
    pan: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    bankName: Optional[str] = ""
    accountNumber: Optional[str] = ""
    ifsc: Optional[str] = ""
    logo: Optional[str] = ""
    signature: Optional[str] = ""
    upiId: Optional[str] = ""
    googleClientId: Optional[str] = ""
    googleDriveFolder: Optional[str] = "GST Billing Invoices"
    paymentAccounts: Optional[list[dict[str, Any]]] = None

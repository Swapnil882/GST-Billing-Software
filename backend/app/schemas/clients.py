from typing import Optional
from pydantic import BaseModel

class ClientBase(BaseModel):
    name: str
    gstin: Optional[str] = ""
    pan: Optional[str] = ""
    address: Optional[str] = ""
    state: Optional[str] = ""
    city: Optional[str] = ""
    pin: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    country: Optional[str] = "India"
    isSEZ: Optional[bool] = False

class ClientCreate(ClientBase):
    id: Optional[str] = None

class ClientResponse(ClientBase):
    id: str

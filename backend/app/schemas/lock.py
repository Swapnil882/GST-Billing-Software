from typing import Optional
from pydantic import BaseModel

class LockStatusResponse(BaseModel):
    enabled: bool
    length: int

class PinVerifyRequest(BaseModel):
    pin: str

class PinSetRequest(BaseModel):
    pin: Optional[str] = None
    currentPin: Optional[str] = None

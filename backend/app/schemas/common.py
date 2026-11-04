from typing import Any, Optional
from pydantic import BaseModel, Field

class SuccessResponse(BaseModel):
    success: bool = True
    id: Optional[str] = None
    message: Optional[str] = None

class ErrorDetail(BaseModel):
    error: str
    code: Optional[str] = None

class HealthResponse(BaseModel):
    ok: bool = True
    version: str
    uptimeSec: int
    pid: int
    hasRecentErrors: bool
    errorsTail: str

class VersionResponse(BaseModel):
    current: str
    latest: Optional[str] = None
    updateAvailable: Optional[bool] = False
    releaseNotes: Optional[str] = None
    releaseUrl: Optional[str] = None

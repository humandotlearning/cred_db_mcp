from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import date, datetime

# --- Base Models ---

class ProviderBase(BaseModel):
    npi: Optional[str] = None
    full_name: str
    dept: Optional[str] = None
    location: Optional[str] = None
    primary_specialty: Optional[str] = None
    is_active: bool = True

class ProviderRead(ProviderBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CredentialBase(BaseModel):
    type: str
    issuer: str
    number: str
    status: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    last_verified_at: Optional[datetime] = None
    metadata_json: Optional[Any] = None

class CredentialRead(CredentialBase):
    id: int
    provider_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AlertRead(BaseModel):
    id: int
    provider_id: int
    message: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Tool IO Models ---

class SyncProviderInput(BaseModel):
    npi: str

class AddCredentialInput(BaseModel):
    provider_id: int
    type: str
    issuer: str
    number: str
    expiry_date: str # Expecting YYYY-MM-DD string as per prompt, or we can parse it

class ListExpiringInput(BaseModel):
    window_days: int
    dept: Optional[str] = None
    location: Optional[str] = None

class ExpiringCredentialItem(BaseModel):
    provider: ProviderRead
    credential: CredentialRead
    days_to_expiry: int
    risk_score: int

class GetSnapshotInput(BaseModel):
    provider_id: Optional[int] = None
    npi: Optional[str] = None

class ProviderSnapshot(BaseModel):
    provider: ProviderRead
    credentials: List[CredentialRead]
    alerts: Optional[List[AlertRead]] = []

class ToolError(BaseModel):
    error: str
    details: Optional[str] = None

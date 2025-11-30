from pydantic import BaseModel
from typing import Optional, List

# Provider Schema
class Provider(BaseModel):
    id: int
    npi: str
    name: str
    # Add other fields as necessary based on CRED_API response

class Credential(BaseModel):
    id: Optional[int] = None
    provider_id: int
    type: str
    issuer: str
    number: str
    expiry_date: str
    # Add other fields as necessary

class ExpiringCredential(BaseModel):
    provider: Provider
    credential: Credential
    days_to_expiry: int
    risk_score: float

class ProviderSnapshot(BaseModel):
    provider: Provider
    credentials: List[Credential]
    alerts: Optional[List[dict]] = None

from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func
from datetime import date, timedelta, datetime
import json

from .models import Provider, Credential, Alert
from .schemas import (
    ProviderRead, CredentialRead, AlertRead,
    ExpiringCredentialItem, ProviderSnapshot
)
from .npi_client import NPIClient

class MCPTools:
    def __init__(self, db: Session):
        self.db = db
        self.npi_client = NPIClient()

    async def sync_provider_from_npi(self, npi: str):
        # 1. Call npi_mcp
        npi_data = await self.npi_client.get_provider_by_npi(npi)

        if not npi_data:
            return {"error": f"NPI {npi} not found in upstream registry"}

        # Map NPI data to our schema.
        # Assuming npi_data has keys: npi, first_name, last_name, taxonomy_desc, practice_address
        # This mapping is hypothetical based on typical NPI registry fields.

        full_name = f"{npi_data.get('first_name', '')} {npi_data.get('last_name', '')}".strip()
        if not full_name:
            full_name = npi_data.get('organization_name', 'Unknown')

        specialty = npi_data.get('taxonomy_desc', 'Unknown')
        address_obj = npi_data.get('practice_address', {})
        # Simple string representation of location
        location = f"{address_obj.get('city', '')}, {address_obj.get('state', '')}" if isinstance(address_obj, dict) else str(address_obj)

        # 2. Update or Create in DB
        provider = self.db.scalar(select(Provider).where(Provider.npi == npi))

        if not provider:
            provider = Provider(
                npi=npi,
                full_name=full_name,
                primary_specialty=specialty,
                location=location,
                is_active=True
            )
            self.db.add(provider)
        else:
            provider.full_name = full_name
            provider.primary_specialty = specialty
            provider.location = location
            # Don't overwrite dept if set locally? assuming upstream doesn't have dept.

        self.db.commit()
        self.db.refresh(provider)

        return ProviderRead.model_validate(provider)

    def add_or_update_credential(
        self, provider_id: int, type: str, issuer: str, number: str, expiry_date: str
    ):
        # Parse expiry_date (assuming YYYY-MM-DD)
        try:
            exp_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
        except ValueError:
             return {"error": "Invalid date format. Use YYYY-MM-DD"}

        # Check provider exists
        provider = self.db.get(Provider, provider_id)
        if not provider:
            return {"error": f"Provider with ID {provider_id} not found"}

        # Find existing credential
        stmt = select(Credential).where(
            and_(
                Credential.provider_id == provider_id,
                Credential.type == type,
                Credential.issuer == issuer,
                Credential.number == number
            )
        )
        credential = self.db.scalar(stmt)

        if credential:
            credential.expiry_date = exp_date
            # Heuristic status update
            credential.status = "active" if exp_date > date.today() else "expired"
            credential.updated_at = datetime.now()
        else:
            credential = Credential(
                provider_id=provider_id,
                type=type,
                issuer=issuer,
                number=number,
                expiry_date=exp_date,
                status="active" if exp_date > date.today() else "expired",
                created_at=datetime.now()
            )
            self.db.add(credential)

        self.db.commit()
        self.db.refresh(credential)

        return CredentialRead.model_validate(credential)

    def list_expiring_credentials(
        self, window_days: int, dept: str | None = None, location: str | None = None
    ):
        today = date.today()
        cutoff = today + timedelta(days=window_days)

        # Build Query
        stmt = select(Credential, Provider).join(Provider).where(
            and_(
                Credential.status == "active",
                Credential.expiry_date <= cutoff,
                Credential.expiry_date >= today # Only future or today (past would be expired)
            )
        )

        if dept:
            stmt = stmt.where(Provider.dept == dept)
        if location:
            stmt = stmt.where(Provider.location.ilike(f"%{location}%"))

        results = self.db.execute(stmt).all()

        output = []
        for cred, prov in results:
            if not cred.expiry_date:
                continue

            days_to_expiry = (cred.expiry_date - today).days

            # Risk Score Heuristic
            # 3 for <30 days, 2 for 30–60, 1 for 60–90
            if days_to_expiry < 30:
                risk_score = 3
            elif days_to_expiry < 60:
                risk_score = 2
            else:
                risk_score = 1

            output.append(ExpiringCredentialItem(
                provider=ProviderRead.model_validate(prov),
                credential=CredentialRead.model_validate(cred),
                days_to_expiry=days_to_expiry,
                risk_score=risk_score
            ))

        return output

    def get_provider_snapshot(
        self, provider_id: int | None = None, npi: str | None = None
    ):
        if not provider_id and not npi:
            return {"error": "Must provide either provider_id or npi"}

        stmt = select(Provider)
        if provider_id:
            stmt = stmt.where(Provider.id == provider_id)
        else:
            stmt = stmt.where(Provider.npi == npi)

        provider = self.db.scalar(stmt)
        if not provider:
            return {"error": "Provider not found"}

        # Get Credentials
        creds = self.db.scalars(
            select(Credential).where(Credential.provider_id == provider.id)
        ).all()

        # Get Alerts (Optional)
        alerts = self.db.scalars(
            select(Alert).where(Alert.provider_id == provider.id)
        ).all()

        return ProviderSnapshot(
            provider=ProviderRead.model_validate(provider),
            credentials=[CredentialRead.model_validate(c) for c in creds],
            alerts=[AlertRead.model_validate(a) for a in alerts]
        )

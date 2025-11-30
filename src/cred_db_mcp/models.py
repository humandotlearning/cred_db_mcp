from datetime import datetime, date
from typing import Optional, List, Any
from sqlalchemy import (
    String, Integer, Boolean, DateTime, Date, ForeignKey, JSON, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

class Provider(Base):
    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    npi: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String)
    dept: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    primary_specialty: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    credentials: Mapped[List["Credential"]] = relationship(
        "Credential", back_populates="provider", cascade="all, delete-orphan"
    )

class Credential(Base):
    __tablename__ = "credentials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("providers.id"), nullable=False
    )
    type: Mapped[str] = mapped_column(String)  # e.g. "state_license", "board_cert"
    issuer: Mapped[str] = mapped_column(String)
    number: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)  # "active", "expired", etc.

    issue_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    metadata_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    provider: Mapped["Provider"] = relationship("Provider", back_populates="credentials")

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("providers.id"))
    message: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    # Minimal schema for alerts as requested

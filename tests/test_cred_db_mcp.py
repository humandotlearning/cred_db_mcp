import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import date, timedelta
import os

from src.cred_db_mcp.main import app, get_db
from src.cred_db_mcp.db import Base
from src.cred_db_mcp.models import Provider, Credential

# Setup in-memory DB for tests
# Use StaticPool to share the in-memory DB across multiple sessions/connections
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def test_client():
    # Create tables once for the module
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    yield client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def clean_tables():
    # Optional: Clear data between tests if needed, but for now just appending is fine
    # as long as IDs/NPIs don't clash or we don't care about accumulation.
    # To be safer, we can delete all data.
    with engine.connect() as conn:
        conn.execute(Credential.__table__.delete())
        conn.execute(Provider.__table__.delete())
        conn.commit()

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    yield db
    db.close()

def test_read_root(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "cred_db_mcp"

def test_add_and_snapshot_provider(test_client, db_session):
    prov = Provider(
        npi="999999", full_name="Test Doc", primary_specialty="General", is_active=True
    )
    db_session.add(prov)
    db_session.commit()

    response = test_client.post(
        "/mcp/tools/get_provider_snapshot",
        json={"npi": "999999"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["provider"]["full_name"] == "Test Doc"
    assert len(data["credentials"]) == 0

def test_add_credential(test_client, db_session):
    # Seed provider
    prov = Provider(
        npi="888888", full_name="Credential Doc", primary_specialty="Surgery", is_active=True
    )
    db_session.add(prov)
    db_session.commit()
    db_session.refresh(prov)

    # Add Credential via tool
    expiry = (date.today() + timedelta(days=100)).strftime("%Y-%m-%d")
    response = test_client.post(
        "/mcp/tools/add_or_update_credential",
        json={
            "provider_id": prov.id,
            "type": "board_cert",
            "issuer": "ABMS",
            "number": "XYZ123",
            "expiry_date": expiry
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["number"] == "XYZ123"
    assert data["status"] == "active"

def test_list_expiring(test_client, db_session):
    # Seed provider
    prov = Provider(
        npi="777777", full_name="Expiring Doc", dept="ER", location="NYC", is_active=True
    )
    db_session.add(prov)
    db_session.commit()
    db_session.refresh(prov)

    # Add expiring credential (in 10 days)
    # expiry date must be a date object for the model
    expiry_1 = date.today() + timedelta(days=10)
    cred = Credential(
        provider_id=prov.id,
        type="license",
        issuer="State",
        number="L1",
        expiry_date=expiry_1,
        status="active"
    )
    db_session.add(cred)

    # Add non-expiring credential (in 100 days)
    expiry_2 = date.today() + timedelta(days=100)
    cred2 = Credential(
        provider_id=prov.id,
        type="license",
        issuer="State",
        number="L2",
        expiry_date=expiry_2,
        status="active"
    )
    db_session.add(cred2)
    db_session.commit()

    # Test tool
    response = test_client.post(
        "/mcp/tools/list_expiring_credentials",
        json={
            "window_days": 30,
            "dept": "ER"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["credential"]["number"] == "L1"
    assert data[0]["days_to_expiry"] == 10
    assert data[0]["risk_score"] == 3  # < 30 days

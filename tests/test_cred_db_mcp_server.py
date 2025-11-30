
import pytest
from unittest.mock import patch, MagicMock
from cred_db_mcp_server.tools import (
    sync_provider_from_npi,
    add_or_update_credential,
    list_expiring_credentials,
    get_provider_snapshot
)
import httpx

# Mock response data
MOCK_PROVIDER = {"id": 1, "npi": "1234567890", "name": "Dr. Test"}
MOCK_CREDENTIAL = {
    "id": 10,
    "provider_id": 1,
    "type": "Medical License",
    "issuer": "State Board",
    "number": "MD12345",
    "expiry_date": "2025-01-01"
}
MOCK_EXPIRING_LIST = [
    {
        "provider": MOCK_PROVIDER,
        "credential": MOCK_CREDENTIAL,
        "days_to_expiry": 30,
        "risk_score": 0.5
    }
]
MOCK_SNAPSHOT = {
    "provider": MOCK_PROVIDER,
    "credentials": [MOCK_CREDENTIAL],
    "alerts": []
}

@patch("cred_db_mcp_server.tools.httpx.Client")
def test_sync_provider_from_npi(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__.return_value = mock_client
    mock_client.post.return_value.status_code = 200
    mock_client.post.return_value.json.return_value = MOCK_PROVIDER

    result = sync_provider_from_npi("1234567890")
    assert result == MOCK_PROVIDER
    mock_client.post.assert_called_once()
    assert "sync_from_npi" in mock_client.post.call_args[0][0]

@patch("cred_db_mcp_server.tools.httpx.Client")
def test_add_or_update_credential(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__.return_value = mock_client
    mock_client.post.return_value.status_code = 200
    mock_client.post.return_value.json.return_value = MOCK_CREDENTIAL

    result = add_or_update_credential(1, "Medical License", "State Board", "MD12345", "2025-01-01")
    assert result == MOCK_CREDENTIAL
    mock_client.post.assert_called_once()
    assert "add_or_update" in mock_client.post.call_args[0][0]

@patch("cred_db_mcp_server.tools.httpx.Client")
def test_list_expiring_credentials(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__.return_value = mock_client
    mock_client.post.return_value.status_code = 200
    mock_client.post.return_value.json.return_value = MOCK_EXPIRING_LIST

    result = list_expiring_credentials(30)
    assert result == MOCK_EXPIRING_LIST
    mock_client.post.assert_called_once()
    assert "expiring" in mock_client.post.call_args[0][0]

@patch("cred_db_mcp_server.tools.httpx.Client")
def test_get_provider_snapshot(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__.return_value = mock_client
    mock_client.post.return_value.status_code = 200
    mock_client.post.return_value.json.return_value = MOCK_SNAPSHOT

    result = get_provider_snapshot(provider_id=1)
    assert result == MOCK_SNAPSHOT
    mock_client.post.assert_called_once()
    assert "snapshot" in mock_client.post.call_args[0][0]

def test_get_provider_snapshot_no_args():
    result = get_provider_snapshot()
    assert "error" in result

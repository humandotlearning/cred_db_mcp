
# Usage of cred_db_mcp

This server provides direct database access and logic for **CredentialWatch** via MCP-compliant tools exposed as HTTP endpoints.

## Agents Usage

Agents can use this server to:
1.  **Onboard new providers**: Call `sync_provider_from_npi` to fetch details from the NPI registry and create a local record.
2.  **Manage Credentials**: Use `add_or_update_credential` to keep license data up to date.
3.  **Monitor Compliance**: Use `list_expiring_credentials` to proactively find providers who need to renew licenses.
4.  **Context Retrieval**: Use `get_provider_snapshot` to get all known data about a provider before answering user questions.

## Running the Server

```bash
# Install dependencies
pip install -e .

# Run
uvicorn src.cred_db_mcp.main:app --reload
```

## Example Tool Call

**Tool:** `list_expiring_credentials`
**Endpoint:** `POST /mcp/tools/list_expiring_credentials`
**Headers:** `Content-Type: application/json`

**Body:**
```json
{
  "window_days": 90,
  "dept": "Cardiology"
}
```

**Response:**
```json
[
  {
    "provider": { "full_name": "Dr. Alice Smith", ... },
    "credential": { "type": "state_license", "expiry_date": "2023-12-01", ... },
    "days_to_expiry": 25,
    "risk_score": 3
  }
]
```

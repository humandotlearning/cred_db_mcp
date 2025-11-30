# CredentialWatch

**CredentialWatch** is a proactive healthcare credential management system built for the **Hugging Face MCP 1st Birthday / Gradio Agents Hackathon**. It leverages the **Model Context Protocol (MCP)**, **LangGraph** agents, **Gradio**, and **Modal** to unify fragmented credential data and alert on upcoming expiries.

## 🎯 Project Goal

CredentialWatch transforms messy, decentralized provider data (state licenses, board certifications, DEA numbers) into:
1.  **A unified, queryable source of truth.**
2.  **A proactive alerting system** for at-risk credentials.

The system is designed to solve the real-world problem of missed credential expiries leading to compliance issues, denied claims, and scheduling conflicts.

## 🧩 Architecture

The system follows a microservice-like architecture with strict separation of concerns, orchestrated by a LangGraph agent.

### Components

1.  **Agent UI (Gradio + LangGraph)**: The user interface where users interact with the agent (chat or sweep triggers).
2.  **Three MCP Servers**:
    *   **`npi_mcp`**: Read-only access to the public NPPES NPI Registry.
    *   **`cred_db_mcp`**: (Hosted in this repo) Internal provider & credential database operations.
    *   **`alert_mcp`**: Alert logging and resolution management.
3.  **Modal Backend**: Hosting FastAPI microservices and the SQLite database (`credentialwatch.db`).

### Data Flow

```
User <-> Gradio UI <-> LangGraph Agent
                            |
           -----------------------------------
           |                |                |
      [npi_mcp]      [cred_db_mcp]     [alert_mcp]
           |                |                |
      (NPI_API)        (CRED_API)       (ALERT_API)
           |                |                |
        NPPES         [SQLite DB]      [SQLite DB]
```

## 📂 Repository Contents: `cred_db_mcp_server`

This repository currently hosts the **Credential Database MCP Server** (`cred_db_mcp`). This component provides the tools necessary for the agent to read from and write to the internal provider/credential database.

### Exposed Tools

The server exposes the following MCP tools (via Gradio's MCP support):

*   **`sync_provider_from_npi(npi)`**:
    *   Syncs a provider's data from the NPI registry (via backend) to the local database.
    *   *Usage*: Onboarding new providers.
*   **`add_or_update_credential(provider_id, type, issuer, number, expiry_date)`**:
    *   Upserts a credential record for a provider.
    *   *Usage*: Keeping license data current.
*   **`list_expiring_credentials(window_days, dept?, location?)`**:
    *   Returns a list of credentials expiring within the specified window (e.g., 90 days).
    *   *Usage*: Proactive monitoring and sweeps.
*   **`get_provider_snapshot(provider_id?, npi?)`**:
    *   Returns provider info + all credentials + alerts.
    *   *Usage*: Context retrieval for user queries.

## 🚀 Getting Started

### Prerequisites

*   **Python 3.11+**
*   **uv** (recommended) or `pip`
*   Access to the **Credential API Backend** (running locally or on Modal).

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/credential-watch-cred-db-mcp.git
    cd credential-watch-cred-db-mcp
    ```

2.  Install dependencies using `uv`:
    ```bash
    uv sync
    ```
    Or with `pip`:
    ```bash
    pip install -e .
    ```

### Configuration

The server requires the backend API URL to be configured. Create a `.env` file in the root directory:

```env
# URL of the backend Credential API service
CRED_API_BASE_URL=http://localhost:8000
```

### Running the Server

Start the Gradio MCP server:

```bash
uv run src/cred_db_mcp_server/main.py
```

The server will launch and:
1.  Open a Gradio UI in your browser (usually `http://127.0.0.1:7860`) where you can manually test the tools.
2.  Expose the MCP endpoints via SSE for the agent to connect to.

## 🧪 Testing

Run the unit tests using `pytest`:

```bash
uv run pytest
```

## 🛠 Tech Stack

*   **Python 3.11**
*   **Gradio 5+** (Frontend & MCP Server)
*   **FastAPI / HTTPX** (Networking)
*   **Pydantic** (Data validation)
*   **uv** (Package management)

---
*Built for the Hugging Face MCP 1st Birthday Hackathon.*

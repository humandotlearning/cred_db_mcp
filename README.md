---
title: CredentialWatch MCP Server
emoji: 🩺
colorFrom: blue
colorTo: purple
sdk: gradio
python_version: 3.11
sdk_version: 6.0.1
app_file: app.py
fullWidth: true
short_description: "Gradio MCP server exposing healthcare credential tools."
tags:
  - mcp
  - gradio
  - tools
  - healthcare
pinned: false
---

# CredentialWatch MCP Server

**CredentialWatch** is a proactive healthcare credential management system built for the **Hugging Face MCP 1st Birthday / Gradio Agents Hackathon**. It leverages the **Model Context Protocol (MCP)**, **LangGraph** agents, **Gradio**, and **Modal** to unify fragmented credential data and alert on upcoming expiries.

## Hugging Face Space

This repository is designed to run as a **Gradio Space**.

- SDK: Gradio (`sdk: gradio` in the README header)
- Entry file: `app.py` (set via `app_file` in the YAML header)
- Python: 3.11+ (pinned with `python_version`)

When you push this repo to a Space with SDK = **Gradio**, the UI and the MCP server will be started automatically.

### Configuration

The server requires the backend Credential API URL to be configured. In your Space settings (or local `.env` file), add:

```env
CRED_API_BASE_URL=http://localhost:8000  # Replace with actual backend URL
```

## MCP Server

This Space exposes its tools via **Model Context Protocol (MCP)** using Gradio.

### How MCP is enabled

In `app.py` we:

- install Gradio with MCP support: `pip install "gradio[mcp]"`
- define typed Python functions with docstrings
- launch the app with MCP support:

```python
demo.launch(mcp_server=True)
```

### MCP endpoints

When the Space is running, Gradio exposes:

- MCP SSE endpoint: `https://<space-host>/gradio_api/mcp/sse`
- MCP schema: `https://<space-host>/gradio_api/mcp/schema`

## Using this Space from an MCP client

### Easiest: Hugging Face MCP Server (no manual config)

1. Go to your HF **MCP settings**: https://huggingface.co/settings/mcp
2. Add this Space under **Spaces Tools** (look for the MCP badge on the Space).
3. Restart your MCP client (VS Code, Cursor, Claude Code, etc.).
4. The tools from this Space will appear as MCP tools and can be called directly.

### Manual config (generic MCP client using mcp-remote)

If your MCP client uses a JSON config, you can point it to the SSE endpoint via `mcp-remote`:

```jsonc
{
  "mcpServers": {
    "credentialwatch": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://<space-host>/gradio_api/mcp/sse"
      ]
    }
  }
}
```

Replace `<space-host>` with the full URL of your Space.

## Local development

```bash
# 1. Install deps
uv sync
# or
pip install -r requirements.txt

# 2. Run locally
uv run python app.py
```

The local server will be available at http://127.0.0.1:7860, and MCP at http://127.0.0.1:7860/gradio_api/mcp/sse.

## Deploying to Hugging Face Spaces

1. Create a new Space with SDK = **Gradio**.
2. Push this repo to the Space (Git or `huggingface_hub`).
3. Ensure the YAML header in `README.md` is present and correct.
4. Wait for the Space to build and start — it should show an **MCP badge** automatically.

## Troubleshooting

- **Configuration error**: Verify `sdk`, `app_file`, and `python_version` in the YAML header. The header must be the first thing in the file (no blank lines before `---`).
- **MCP badge missing**: Check that your app calls `demo.launch(mcp_server=True)` and confirm the Space is public.
- **LFS issues**: Ensure `README.md` is NOT tracked via Git LFS.

---

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

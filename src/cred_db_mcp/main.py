from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Union

from .db import get_db, init_db
from .mcp_tools import MCPTools
from .schemas import (
    SyncProviderInput, AddCredentialInput, ListExpiringInput, GetSnapshotInput,
    ProviderRead, CredentialRead, ExpiringCredentialItem, ProviderSnapshot, ToolError
)

app = FastAPI(title="CredentialWatch DB MCP", version="0.1.0")

# Initialize DB on startup (for simple deployments)
@app.on_event("startup")
def on_startup():
    init_db()

def get_mcp_tools(db: Session = Depends(get_db)) -> MCPTools:
    return MCPTools(db)

# --- MCP Tool Endpoints ---
# Pattern: /mcp/tools/{tool_name}
# We use POST for all of them as they are "function calls"

@app.post("/mcp/tools/sync_provider_from_npi", response_model=Union[ProviderRead, ToolError])
async def sync_provider_from_npi(
    args: SyncProviderInput,
    tools: MCPTools = Depends(get_mcp_tools)
):
    """
    Syncs provider data from the NPI Registry via npi_mcp.
    """
    result = await tools.sync_provider_from_npi(args.npi)
    if isinstance(result, dict) and "error" in result:
        # Return generic error structure instead of 400 for agent handling if preferred,
        # but usually 400 is better for HTTP.
        # The prompt says "return a structured error".
        return ToolError(error=result["error"])
    return result

@app.post("/mcp/tools/add_or_update_credential", response_model=Union[CredentialRead, ToolError])
def add_or_update_credential(
    args: AddCredentialInput,
    tools: MCPTools = Depends(get_mcp_tools)
):
    """
    Adds or updates a credential record.
    """
    result = tools.add_or_update_credential(
        provider_id=args.provider_id,
        type=args.type,
        issuer=args.issuer,
        number=args.number,
        expiry_date=args.expiry_date
    )
    if isinstance(result, dict) and "error" in result:
        return ToolError(error=result["error"])
    return result

@app.post("/mcp/tools/list_expiring_credentials", response_model=List[ExpiringCredentialItem])
def list_expiring_credentials(
    args: ListExpiringInput,
    tools: MCPTools = Depends(get_mcp_tools)
):
    """
    Lists credentials expiring within a window.
    """
    return tools.list_expiring_credentials(
        window_days=args.window_days,
        dept=args.dept,
        location=args.location
    )

@app.post("/mcp/tools/get_provider_snapshot", response_model=Union[ProviderSnapshot, ToolError])
def get_provider_snapshot(
    args: GetSnapshotInput,
    tools: MCPTools = Depends(get_mcp_tools)
):
    """
    Gets a full snapshot of a provider.
    """
    result = tools.get_provider_snapshot(
        provider_id=args.provider_id,
        npi=args.npi
    )
    if isinstance(result, dict) and "error" in result:
        return ToolError(error=result["error"])
    return result

# Simple info endpoint
@app.get("/")
def read_root():
    return {
        "service": "cred_db_mcp",
        "status": "running",
        "docs": "/docs"
    }

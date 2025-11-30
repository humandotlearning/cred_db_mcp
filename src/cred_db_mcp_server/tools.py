"""
This module implements the tools exposed by the MCP server.
Each function corresponds to an MCP tool.
"""
import httpx
from typing import Optional, List, Dict, Any
from .config import CRED_API_BASE_URL
# from .schemas import Provider, Credential, ExpiringCredential, ProviderSnapshot

# We can use simple types in signature for Gradio MCP compatibility
# but use schemas for internal validation if needed.
# Since the prompt asked for mapped errors, we'll wrap calls.

def sync_provider_from_npi(npi: str) -> Dict[str, Any]:
    """
    Syncs a provider's data from the NPI registry.

    Args:
        npi (str): The NPI number of the provider.

    Returns:
        dict: The provider object returned by the API.
    """
    url = f"{CRED_API_BASE_URL}/providers/sync_from_npi"
    try:
        with httpx.Client() as client:
            response = client.post(url, json={"npi": npi})
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        # Map HTTP errors to MCP/User friendly errors
        if e.response.status_code == 404:
            return {"error": f"Provider with NPI {npi} not found or sync failed."}
        return {"error": f"API Error: {e.response.text}"}
    except Exception as e:
        return {"error": f"Connection Error: {str(e)}"}

def add_or_update_credential(
    provider_id: int,
    type: str,
    issuer: str,
    number: str,
    expiry_date: str
) -> Dict[str, Any]:
    """
    Adds or updates a credential for a provider.

    Args:
        provider_id (int): The internal ID of the provider.
        type (str): The type of credential (e.g., 'Medical License').
        issuer (str): The issuing body (e.g., 'State Board').
        number (str): The credential number.
        expiry_date (str): The expiry date in YYYY-MM-DD format.

    Returns:
        dict: The created or updated credential object.
    """
    url = f"{CRED_API_BASE_URL}/credentials/add_or_update"
    payload = {
        "provider_id": provider_id,
        "type": type,
        "issuer": issuer,
        "number": number,
        "expiry_date": expiry_date
    }
    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"API Error: {e.response.text}"}
    except Exception as e:
        return {"error": f"Connection Error: {str(e)}"}

def list_expiring_credentials(
    window_days: int,
    dept: Optional[str] = None,
    location: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Lists credentials expiring within a certain number of days.

    Args:
        window_days (int): The number of days to check for expiry.
        dept (str, optional): Filter by department.
        location (str, optional): Filter by location.

    Returns:
        list: A list of objects containing provider, credential, days_to_expiry, and risk_score.
    """
    url = f"{CRED_API_BASE_URL}/credentials/expiring"
    payload = {
        "window_days": window_days,
        "dept": dept,
        "location": location
    }
    # Remove None values to avoid sending them if API doesn't expect them or treat them as valid
    payload = {k: v for k, v in payload.items() if v is not None}

    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        # In case of error, return a list with an error dict or raise
        # For MCP, returning structured error info is usually better than crashing
        # But for list return type, we might need to handle differently.
        # Here we assume the tool call handles exceptions or checks for "error" key in result if it was a dict.
        # Since return type is List, we can't easily return a dict error.
        # We'll return an empty list and print error or raise.
        # Let's raise ValueError which Gradio might catch and show.
        raise ValueError(f"API Error: {e.response.text}")
    except Exception as e:
        raise ConnectionError(f"Connection Error: {str(e)}")

def get_provider_snapshot(
    provider_id: Optional[int] = None,
    npi: Optional[str] = None
) -> Dict[str, Any]:
    """
    Gets a snapshot of a provider's data including credentials and alerts.

    Args:
        provider_id (int, optional): The provider's internal ID.
        npi (str, optional): The provider's NPI.

    Returns:
        dict: Object containing provider details, credentials, and alerts.
    """
    if provider_id is None and npi is None:
        return {"error": "Must provide either provider_id or npi."}

    url = f"{CRED_API_BASE_URL}/providers/snapshot"
    payload = {}
    if provider_id is not None:
        payload["provider_id"] = provider_id
    if npi is not None:
        payload["npi"] = npi

    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": "Provider not found."}
        return {"error": f"API Error: {e.response.text}"}
    except Exception as e:
        return {"error": f"Connection Error: {str(e)}"}

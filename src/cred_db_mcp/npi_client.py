import os
import httpx
from typing import Optional, Dict, Any

class NPIClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("NPI_MCP_URL", "http://localhost:8001")
        # Ensure no trailing slash
        self.base_url = self.base_url.rstrip("/")

    async def get_provider_by_npi(self, npi: str) -> Optional[Dict[str, Any]]:
        """
        Calls the npi_mcp server to get provider details.
        Assumes npi_mcp exposes a tool 'get_provider_by_npi' via HTTP.

        The NPI MCP is expected to have a similar structure: POST /mcp/tools/get_provider_by_npi
        """
        url = f"{self.base_url}/mcp/tools/get_provider_by_npi"

        # We assume the NPI MCP accepts arguments in the body
        payload = {"npi": npi}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10.0)

                if response.status_code == 200:
                    data = response.json()
                    # If the tool wraps return value, e.g. {"result": ...} adjust here.
                    # For now assuming direct return or generic tool response.
                    return data
                elif response.status_code == 404:
                    return None
                else:
                    # Log error or raise
                    print(f"Error calling NPI MCP: {response.status_code} {response.text}")
                    return None
        except httpx.RequestError as e:
             print(f"Request error calling NPI MCP: {e}")
             return None

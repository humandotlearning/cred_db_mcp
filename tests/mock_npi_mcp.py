from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class NpiRequest(BaseModel):
    npi: str

@app.post("/mcp/tools/get_provider_by_npi")
def get_provider_by_npi(req: NpiRequest):
    if req.npi == "1234567890":
        return {
            "npi": "1234567890",
            "first_name": "John",
            "last_name": "Doe",
            "taxonomy_desc": "Cardiology",
            "practice_address": {
                "city": "New York",
                "state": "NY"
            }
        }
    return None

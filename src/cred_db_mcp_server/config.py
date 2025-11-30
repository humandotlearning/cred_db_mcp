import os
from dotenv import load_dotenv

load_dotenv()

CRED_API_BASE_URL = os.getenv("CRED_API_BASE_URL", "http://localhost:8000")

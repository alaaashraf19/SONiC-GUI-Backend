from fastapi import HTTPException
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
 
SONIC_BASE_URL = os.getenv("SONIC_BASE_URL")


RESTCONF_HEADERS = {
    "Accept": "application/yang-data+json"
}

async def fetch_vlans():
    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            response = await client.get(
                f"{SONIC_BASE_URL}/restconf/data/sonic-vlan:sonic-vlan",
                headers=RESTCONF_HEADERS,
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

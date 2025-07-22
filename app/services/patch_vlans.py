from fastapi import HTTPException
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
 
SONIC_BASE_URL = os.getenv("SONIC_BASE_URL")
USERNAME = os.getenv("SONIC_USERNAME")
PASSWORD = os.getenv("SONIC_PASSWORD")

RESTCONF_HEADERS = {
    "Accept": "application/yang-data+json"
}

async def update_vlans(vlan_data: dict):
    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            response = await client.patch(
                f"{SONIC_BASE_URL}/restconf/data/sonic-vlan:sonic-vlan",
                headers=RESTCONF_HEADERS,
                json=vlan_data,  
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

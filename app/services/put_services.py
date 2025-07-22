import httpx
import os
from dotenv import load_dotenv

load_dotenv()

SONIC_BASE_URL = os.getenv("SONIC_BASE_URL")

RESTCONF_HEADERS = {
    "Content-Type": "application/yang-data+json"
}

async def put_vlan(vlan_payload: dict):
    if not SONIC_BASE_URL:
        raise Exception("SONIC_BASE_URL not set in .env")

    url = f"{SONIC_BASE_URL}/restconf/data/sonic-vlan:sonic-vlan"

    async with httpx.AsyncClient(verify=False) as client:
        response = await client.put(
            url,
            headers=RESTCONF_HEADERS,
            json=vlan_payload
        )
        if response.status_code in [200, 201, 204]:
            return {"status": "success", "message": "VLAN configuration updated"}
        else:
            raise Exception(f"Failed to update VLANs: {response.status_code} - {response.text}")

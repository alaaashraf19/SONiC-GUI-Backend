from http.client import HTTPException
from dotenv import load_dotenv
import httpx, os

RESTCONF_HEADERS = {
    "Accept": "application/yang-data+json"
}


load_dotenv()
SONIC_SWITCH_IP=os.getenv("SONIC_SWITCH_IP")
SONIC_BASE_URL=os.getenv("SONIC_BASE_URL")


async def get_po_service():
    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            response = await client.get(
                f"{SONIC_BASE_URL}/restconf/data/sonic-port-oper:sonic-port-oper",
                headers=RESTCONF_HEADERS
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

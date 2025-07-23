import httpx
from fastapi import HTTPException

SWITCH_IP = "https://10.1.114.81:443"
BASE_URL = f"{SWITCH_IP}/restconf/data/sonic-vlan:sonic-vlan"
HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}

AUTH = ("admin", "sonic") 

async def delete_all_vlans_from_switch():
    try:
        print(f"[DEBUG] Sending DELETE request to {BASE_URL}")
        async with httpx.AsyncClient(verify=False) as client:
            delete_response = await client.delete(BASE_URL, headers=HEADERS, auth=AUTH, timeout=5.0)

        print(f"[DEBUG] Status: {delete_response.status_code}")
        print(f"[DEBUG] Response: {delete_response.text}")

        if delete_response.status_code == 204:
            return {"detail": "All VLANs deleted from switch successfully."}
        else:
            raise HTTPException(
                status_code=delete_response.status_code,
                detail=f"Switch responded with: {delete_response.text}"
            )

    except httpx.RequestError as exc:
        print(f"[ERROR] Request failed: {exc}")
        raise HTTPException(status_code=500, detail=f"Request failed: {exc}")

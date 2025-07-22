from fastapi import APIRouter, HTTPException
from app.services.put_services import put_vlan  
from pydantic import BaseModel
from typing import List, Optional
from app.models.vlan import VLan_request


router = APIRouter()

@router.put("/vlan", tags=["vlans"])
async def update_vlan(payload: VLan_request):
    try:
        # Restructure it to match the switch's expected payload
        formatted_payload = {
            "sonic-vlan:sonic-vlan": {
                "VLAN": payload.vlan.dict(by_alias=True),
                "VLAN_MEMBER": payload.members.dict(by_alias=True)
            }
        }
        return await put_vlan(formatted_payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

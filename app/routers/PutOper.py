from fastapi import APIRouter, HTTPException
from app.services.put_services import put_vlan  
from pydantic import BaseModel
from typing import List, Optional


router = APIRouter()

# Define your Pydantic models
class VlanMember(BaseModel):
    name: str
    ifname: str
    tagging_mode: str

class VlanListItem(BaseModel):
    name: str
    vlanid: int
    description: Optional[str] = None
    mac_learning: Optional[str] = "enabled"

class VlanData(BaseModel):
    VLAN_LIST: List[VlanListItem]
    VLAN_MEMBER_LIST: List[VlanMember]

class SonicVlanPayload(BaseModel):
    VLAN: VlanData

# Define your endpoint
@router.put("/vlan", tags=["vlans"])
async def update_vlan(payload: dict):
    try:
        result = await put_vlan(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

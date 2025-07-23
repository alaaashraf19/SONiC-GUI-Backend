from fastapi import APIRouter, HTTPException
from app.services.DeleteServices import delete_all_vlans_from_switch

delete_oper_vlan_router = APIRouter()

@delete_oper_vlan_router.delete("/delete/all-vlan-config", summary="Delete ALL VLAN config (VLANs + Members)")
async def delete_all_vlan_config():
    try:
        return await delete_all_vlans_from_switch()
    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")

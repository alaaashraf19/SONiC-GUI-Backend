from fastapi import APIRouter, HTTPException
from app.services.DeleteServices import delete_all_vlans_from_switch,delete_vlan_by_name,delete_vlan_description_by_name


delete_oper_vlan_router = APIRouter()

@delete_oper_vlan_router.delete("/delete/all-vlan-config", summary="Delete ALL VLAN config (VLANs + Members)")
async def delete_all_vlan_config():
    try:
        return await delete_all_vlans_from_switch()
    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")
    
@delete_oper_vlan_router.delete("/delete/vlan/{vlan_name}", summary="Delete a single VLAN by name")
async def delete_single_vlan(vlan_name: str):
    return await delete_vlan_by_name(vlan_name)    


@delete_oper_vlan_router.delete(
    "/delete/vlan-description/{vlan_name}", summary="Delete VLAN description by name"
)
async def delete_vlan_description(vlan_name: str):
    return await delete_vlan_description_by_name(vlan_name)
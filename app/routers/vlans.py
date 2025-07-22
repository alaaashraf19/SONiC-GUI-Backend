from fastapi import APIRouter, HTTPException
from app.services.sonic_services import fetch_vlans
from app.services.patch_vlans import update_vlans


router = APIRouter()


@router.get("/")
async def get_vlans():
 return await fetch_vlans()   

@router.patch("/patch")
async def patch_vlans(vlan_data):
    return await update_vlans(vlan_data)

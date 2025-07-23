from fastapi import APIRouter, HTTPException
from app.services.fetch_vlans import fetch_vlans
from app.services.patch_vlans import update_vlans
from fastapi import Body


router = APIRouter()


@router.get("/")
async def get_vlans():
 return await fetch_vlans()   

@router.patch("/patch")
async def patch_vlans(vlan_data: dict = Body(...)): 
    return await update_vlans(vlan_data)

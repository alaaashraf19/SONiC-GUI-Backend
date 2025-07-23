from fastapi import APIRouter
from app.services.sonic_services import fetch_vlans
from app.models.vlan import Vlan_request
from app.services.post_Vlans import add_vlans
router = APIRouter()



@router.get("/")
async def get_vlans():
    return await fetch_vlans()   


@router.post("/add_vlans")
async def add(request:Vlan_request):
    return await add_vlans(request) 

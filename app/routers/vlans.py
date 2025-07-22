from fastapi import APIRouter, HTTPException
import httpx
from dotenv import load_dotenv
import os
from app.services.sonic_services import fetch_vlans
from app.services.patch_vlans import update_vlans


router = APIRouter()

RESTCONF_HEADERS = {
    "Accept": "application/yang-data+json"
}

load_dotenv()

SONIC_SWITCH_IP = os.getenv("SONIC_SWITCH_IP")
SONIC_BASE_URL = os.getenv("SONIC_BASE_URL")


@router.get("/")
async def get_vlans():
 return await fetch_vlans()   

@router.patch("/patch")
async def patch_vlans(vlan_data):
    return await update_vlans(vlan_data)

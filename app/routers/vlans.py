from fastapi import APIRouter, HTTPException
import httpx
from dotenv import load_dotenv
import os
from app.services.sonic_services import fetch_vlans

router = APIRouter()

RESTCONF_HEADERS = {
    "Accept": "application/yang-data+json"
}

load_dotenv()

SONIC_SWITCH_IP = os.getenv("SONIC_SWITCH_IP")
SONIC_BASE_URL = os.getenv("SONIC_BASE_URL")


@router.get("/vlans")
async def get_vlans():
 return await fetch_vlans()   
import os
from fastapi import APIRouter
from dotenv import load_dotenv
from app.services.port_op_services import get_po_service


router = APIRouter()

load_dotenv()
SONIC_SWITCH_IP=os.getenv("SONIC_SWITCH_IP")

@router.get("/")
async def root():
    return {
        "message": "SONiC RESTCONF GET Request Demo",
        "switch_ip": SONIC_SWITCH_IP,
        "endpoint": "/restconf/data/sonic-port-oper:sonic-port-oper" 
    }

@router.get("/po")
async def get_port_oper():
    return await get_po_service()
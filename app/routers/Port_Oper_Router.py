import os
from fastapi import APIRouter
from app.services.Get_Port_Op_Services import get_po_service


router = APIRouter()



@router.get("/")
async def get_port_oper():
    return await get_po_service()
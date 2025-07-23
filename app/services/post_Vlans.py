import re, os
from app.models.vlan import Vlan_request
from fastapi import HTTPException
from typing import List
from dotenv import load_dotenv

RESTCONF_HEADERS = {
    "Accept": "application/yang-data+json"
}


load_dotenv()
SONIC_SWITCH_IP=os.getenv("SONIC_SWITCH_IP")
SONIC_BASE_URL=os.getenv("SONIC_BASE_URL")



def is_valid_vlan_name(name: str) -> bool:
    return re.fullmatch(r'Vlan\d+', name) is not None

def extractNumbers_VlanName(name:str):
    id = re.match(r'^[A-Za-z]+(\d+)$', name)
    if id:
        return int(id.group(1))
    return None
    
async def add_vlans(request:Vlan_request):

    # if request.vlan.VLAN_LIST[0].name[0].islower():

    vlan_List= request.vlan.VLAN_LIST
    member_List= request.members.VLAN_MEMBER_LIST
    for i in vlan_List:
        if not is_valid_vlan_name(i.name):
            raise HTTPException(status_code=400, detail= "VLAN name format: 'Vlanxxx'")
        
    for i in vlan_List:
        extracted_name_vlan_id= extractNumbers_VlanName(i.name)
        if not extracted_name_vlan_id: #could be none
            raise HTTPException(status_code=400, detail="VLAN name must include the id after it")
        
        if i.vlanid != extracted_name_vlan_id:
            raise HTTPException(status_code=400, detail="VLAN id does not match id in name")

        
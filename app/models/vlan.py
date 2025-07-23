from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator

class Vlan(BaseModel):
    name: str
    vlanid: int
    description: Optional[str]
    mac_learning: Literal["enabled", "disabled"]

class Vlan_memberList(BaseModel):
    name: str
    ifname: str
    tagging_mode: Literal["untagged", "tagged"]

class SonicVLAN(BaseModel):
    VLAN_LIST: List[Vlan]

class SonicVLANMember(BaseModel):
    VLAN_MEMBER_LIST: Optional[List[Vlan_memberList]]=None


class Vlan_request(BaseModel):
    vlan: SonicVLAN = Field(..., alias="sonic-vlan:VLAN")
    members: Optional[SonicVLANMember] = Field(None, alias="sonic-vlan:VLAN_MEMBER")

    @model_validator(mode = 'before')
    def check_vlans_members(cls, values):
        vlan_data = values.get("sonic-vlan:VLAN")
        if not vlan_data or not vlan_data.get("VLAN_LIST"):
            raise ValueError("sonic-vlan:VLAN wiht VLAN_LIST is required")
        return values

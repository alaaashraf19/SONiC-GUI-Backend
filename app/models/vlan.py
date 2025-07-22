from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field

class Vlan(BaseModel):
    name: str
    vlanid: int
    description: Optional[str]
    mac_learning: Literal["enabled", "disabled"]

class VLan_memberList(BaseModel):
    name: str
    ifname: str
    tagging_mode: Literal["untagged", "tagged"]

class SonicVLAN(BaseModel):
    VLAN_LIST: List[Vlan]

class SonicVLANMember(BaseModel):
    VLAN_MEMBER_LIST: List[VLan_memberList]


class VLan_request(BaseModel):
    vlan: SonicVLAN = Field(..., alias="sonic-vlan:VLAN")
    members: SonicVLANMember = Field(..., alias="sonic-vlan:VLAN_MEMBER")

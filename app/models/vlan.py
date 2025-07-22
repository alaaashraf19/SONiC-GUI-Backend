from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field, model_validator
import re


class Vlan(BaseModel):
    name: str
    vlanid: int
    description: Optional[str]
    mac_learning: Literal["enabled", "disabled"]

    @model_validator(mode="after")
    def check_vlan_name_matches_id(cls, values: "Vlan"):
        match = re.match(r"Vlan(\d+)", values.name)
        if not match:
            raise ValueError(f"Invalid VLAN name format: {values.name}. Expected format: 'Vlan<id>'")
        
        name_id = int(match.group(1))
        if name_id != values.vlanid:
            raise ValueError(f"VLAN name '{values.name}' does not match vlanid {values.vlanid}")
        
        return values

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

    @model_validator(mode="after")
    def validate_vlan_name_match(cls, values: "VLan_request"):
        vlan_list = values.vlan.VLAN_LIST
        member_list = values.members.VLAN_MEMBER_LIST

        vlan_names = {v.name for v in vlan_list}
        member_names = {m.name for m in member_list}

        if vlan_names != member_names:
            raise ValueError("VLAN names and VLAN_MEMBER names must match exactly.")

        return values

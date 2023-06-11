"""models for Membership"""
from typing import Optional

from pydantic import BaseModel

from id_base_model.schemas import IntIDBaseModel


class Membership(IntIDBaseModel):
    """
    Pydantic model for Membership
    """

    group_id: int
    item_id: int

    class Config:
        orm_mode = True


class MembershipCreate(BaseModel):
    group_id: int
    item_id: int


class MembershipUpdate(BaseModel):
    group_id: Optional[int] = None
    item_id: Optional[int] = None

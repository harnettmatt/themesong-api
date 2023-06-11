"""models for Group"""
from typing import List, Optional

from pydantic import BaseModel

from id_base_model.schemas import IntIDBaseModel
from item.schemas import Item


class Group(IntIDBaseModel):
    """
    Pydantic model for Group
    """

    name: str
    items: List[Item] = []
    # TODO: https://github.com/harnettmatt/rankings/issues/54
    # author: User

    class Config:
        orm_mode = True


class GroupCreate(BaseModel):
    name: str
    # TODO: https://github.com/harnettmatt/rankings/issues/54
    # author: User


class GroupUpdate(BaseModel):
    name: Optional[str] = None

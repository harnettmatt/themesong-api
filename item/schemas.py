"""models for Item"""

from typing import Optional

from pydantic import BaseModel

from id_base_model.schemas import IntIDBaseModel


class Item(IntIDBaseModel):
    """
    Pydantic model for Item
    """

    name: str

    class Config:
        orm_mode = True


class ItemCreate(BaseModel):
    name: str


class ItemUpdate(BaseModel):
    name: Optional[str]

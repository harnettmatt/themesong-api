"""Module containing IDBaseModel intended for extension"""

from pydantic import BaseModel


class IntIDBaseModel(BaseModel):
    """
    Pydantic model with id field of type int
    """

    id: int


class StrIDBaseModel(BaseModel):
    """
    Pydantic model with id field of type string
    """

    id: str

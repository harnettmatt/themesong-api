"""Module containing IDBaseModel intended for extension"""

from pydantic import BaseModel


class CustomBaseModel(BaseModel):
    class Config:
        use_enum_values = True


class IntIDBaseModel(CustomBaseModel):
    """
    Pydantic model with id field of type int
    """

    id: int


class StrIDBaseModel(CustomBaseModel):
    """
    Pydantic model with id field of type string
    """

    id: str

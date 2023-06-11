"""models for User"""
from pydantic import BaseModel

from id_base_model.schemas import StrIDBaseModel


class User(StrIDBaseModel):
    """
    Pydantic model for User
    """

    class Config:
        # TODO: should this be moved to IDBaseModel
        orm_mode = True


class UserCreate(BaseModel):
    id: str


# uncomment when patching is supported
# class UserUpdate(BaseModel):

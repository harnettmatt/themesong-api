"""models for User"""
from id_base_model.schemas import IntIDBaseModel
from strava.schemas import StravaUserInfo


class User(IntIDBaseModel):
    """
    Pydantic model for User
    """

    strava_user_info: StravaUserInfo

    class Config:
        orm_mode = True


class UserCreate(IntIDBaseModel):
    pass


# uncomment when patching is supported
# class UserUpdate(BaseModel):

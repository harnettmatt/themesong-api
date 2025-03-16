"""models for User"""
from app.id_base_model.schemas import IntIDBaseModel
from app.strava.schemas import StravaUserInfo


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
# class UserUpdate(CustomBaseModel):

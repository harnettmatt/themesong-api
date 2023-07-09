from enum import Enum

from pydantic import BaseModel


class RequestGrantType(Enum):
    AUTHORIZATION_CODE = "authorization_code"
    REFRESH_TOKEN = "refresh_token"


class APIUserInfo(BaseModel):
    access_token: str
    refresh_token: str

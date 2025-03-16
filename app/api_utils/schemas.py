from datetime import datetime
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, root_validator, validator


class RequestGrantType(str, Enum):
    AUTHORIZATION_CODE = "authorization_code"
    REFRESH_TOKEN = "refresh_token"


class APIUserInfo(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: datetime


class APIAuthParams(BaseModel):
    response_type: str = "code"
    client_id: Union[str, int]
    redirect_uri: str
    scope: str
    state: str


class APITokenRequest(BaseModel):
    refresh_token: Optional[str] = None
    code: Optional[str] = None
    grant_type: RequestGrantType = RequestGrantType.AUTHORIZATION_CODE

    # class Config:
    #     use_enum_values = True

    @root_validator(pre=True)
    def validate_code_or_refresh_token(cls, values):
        if values.get("refresh_token") and values.get("code"):
            raise ValueError("code and refresh_token cannot both be provided")
        if not values.get("refresh_token") and not values.get("code"):
            raise ValueError("code or refresh_token must be provided")
        return values

    @validator("grant_type", always=True)
    def validate_grant_type(cls, v, values):
        if values.get("refresh_token"):
            return RequestGrantType.REFRESH_TOKEN
        if values.get("code"):
            return RequestGrantType.AUTHORIZATION_CODE

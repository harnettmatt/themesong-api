"""schemas for Strava"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from id_base_model.schemas import IntIDBaseModel
from settings import ENV_VARS


class StravaAspectType(Enum):
    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"


class StravaObjectType(Enum):
    ACTIVITY = "activity"
    ATHLETE = "athlete"


class StravaWebhookInput(BaseModel):
    aspect_type: StravaAspectType
    event_time: datetime
    object_id: int  # activity id or athelete id depending on object_type
    object_type: StravaObjectType
    owner_id: int  # athlete id
    subscription_id: int
    updates: Optional[dict] = None  # TODO: not sure if this is the right type


class StravaOAauthTokenRequest(BaseModel):
    client_id: int = ENV_VARS.STRAVA_CLIENT_ID
    client_secret: str = ENV_VARS.STRAVA_CLIENT_SECRET
    code: str
    grant_type: str = "authorization_code"


class StravaAthlete(IntIDBaseModel):
    username: str
    firstname: str
    lastname: str
    # TODO: what other attributes should i load in


class StravaAuth(BaseModel):
    # token_type: str
    expires_at: datetime
    # expires_in: timedelta
    refresh_token: str
    access_token: str


class StravaUserInfo(IntIDBaseModel, StravaAuth):
    user_id: int

    class Config:
        orm_mode = True


class StravaOAuthTokenResponse(StravaAuth):
    athlete: StravaAthlete


class StravaActivity(BaseModel):
    # TODO: write a property field that calculated the end
    id: int
    start_date: datetime
    elapsed_time: int
    description: Optional[str]


class StravaActivityStream(BaseModel):
    pass

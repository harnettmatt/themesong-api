"""schemas for Strava"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from urllib.parse import urlencode

from pydantic import BaseModel, validator

from app import settings
from app.api_utils.schemas import APIAuthParams, APITokenRequest, APIUserInfo
from app.api_utils.timezone_aware import self_aware_datetime
from app.id_base_model.schemas import IntIDBaseModel, StrIDBaseModel


class StravaAspectType(str, Enum):
    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"


class StravaObjectType(str, Enum):
    ACTIVITY = "activity"
    ATHLETE = "athlete"


class StravaStreamKeys(str, Enum):
    TIME = "time"
    HEARTRATE = "heartrate"


class StravaAuthStateParam(StrIDBaseModel):
    pass


class StravaAuthParams(APIAuthParams):
    client_id: int = settings.ENV_VARS.STRAVA_CLIENT_ID
    redirect_uri: str = f"{settings.ENV_VARS.HOST}/strava/authorization"
    scope: str = "activity:read_all,activity:write"
    approval_prompt: str = "force"

    def format_as_url(self) -> str:
        return f"http://www.strava.com/oauth/authorize?{urlencode(self.dict())}"


class StravaWebhookInput(BaseModel):
    aspect_type: StravaAspectType
    object_id: int  # activity id or athelete id depending on object_type
    object_type: StravaObjectType
    owner_id: int  # athlete id


class StravaTokenRequest(APITokenRequest):
    client_id: int = settings.ENV_VARS.STRAVA_CLIENT_ID
    client_secret: str = settings.ENV_VARS.STRAVA_CLIENT_SECRET


class StravaAthlete(IntIDBaseModel):
    username: str
    firstname: str
    lastname: str


class StravaAuth(APIUserInfo):
    # token_type: str
    expires_at: datetime
    # expires_in: timedelta

    @validator("expires_at", always=True)
    def self_aware_datetime(cls, value: datetime) -> datetime:
        return self_aware_datetime(value)


class StravaUserInfo(IntIDBaseModel, StravaAuth):
    user_id: int

    class Config:
        orm_mode = True


class StravaTokenResponse(StravaAuth):
    athlete: StravaAthlete


class StravaActivity(BaseModel):
    id: int
    start_date: datetime
    description: Optional[str] = None

    @validator("start_date", always=True)
    def self_aware_datetime(cls, value: datetime) -> datetime:
        return self_aware_datetime(value)


class StravaActivityStreamData(BaseModel):
    data: list[float]


class StravaActivityStream(BaseModel):
    heartrate: StravaActivityStreamData
    time: StravaActivityStreamData

    def get_max_heartrate(self) -> Optional[tuple[int, float]]:
        if len(self.heartrate.data) == 0:
            return None
        max_heartrate = max(self.heartrate.data)
        max_heartrate_index = self.heartrate.data.index(max_heartrate)

        return max_heartrate_index, max_heartrate

    def get_max_heartrate_time_mark(self) -> Optional[timedelta]:
        heart_rate_tuple = self.get_max_heartrate()
        if heart_rate_tuple is None:
            return None
        if len(self.time.data) == 0:
            return None

        (index, _) = heart_rate_tuple
        seconds_elapsed = self.time.data[index]

        return timedelta(seconds=seconds_elapsed)

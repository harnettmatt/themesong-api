"""schemas for Strava"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from api_utils.schemas import APITokenRequest, APIUserInfo
from id_base_model.schemas import IntIDBaseModel
from settings import ENV_VARS


class StravaAspectType(Enum):
    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"


class StravaObjectType(Enum):
    ACTIVITY = "activity"
    ATHLETE = "athlete"


class StravaStreamKeys(Enum):
    TIME = "time"
    HEARTRATE = "heartrate"


class StravaWebhookInput(BaseModel):
    aspect_type: StravaAspectType
    event_time: datetime
    object_id: int  # activity id or athelete id depending on object_type
    object_type: StravaObjectType
    owner_id: int  # athlete id
    subscription_id: int
    updates: Optional[dict] = None  # FIXME: not sure if this is the right type


class StravaTokenRequest(APITokenRequest):
    client_id: int = ENV_VARS.STRAVA_CLIENT_ID
    client_secret: str = ENV_VARS.STRAVA_CLIENT_SECRET


class StravaAthlete(IntIDBaseModel):
    username: str
    firstname: str
    lastname: str


class StravaAuth(APIUserInfo):
    # token_type: str
    expires_at: datetime
    # expires_in: timedelta


class StravaUserInfo(IntIDBaseModel, StravaAuth):
    user_id: int

    class Config:
        orm_mode = True


class StravaTokenResponse(StravaAuth):
    athlete: StravaAthlete


class StravaActivity(BaseModel):
    id: int
    start_date: datetime
    elapsed_time: int
    description: Optional[str]


class StravaActivityStreamData(BaseModel):
    data: list[float]


class StravaActivityStream(BaseModel):
    heartrate: StravaActivityStreamData
    time: StravaActivityStreamData

    def get_max_heartrate(self) -> Optional[float]:
        if len(self.heartrate.data) == 0:
            return None
        return max(self.heartrate.data)

    def get_max_heartrate_time_mark(self) -> Optional[timedelta]:
        max_heartrate = self.get_max_heartrate()
        if max_heartrate is None:
            return None
        if len(self.time.data) == 0:
            return None

        max_heartrate_index = self.heartrate.data.index(max_heartrate)
        seconds_elapsed = self.time.data[max_heartrate_index]

        return timedelta(seconds=seconds_elapsed)

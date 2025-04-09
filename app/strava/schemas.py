"""schemas for Strava"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from urllib.parse import urlencode

from app import settings
from app.api_utils.schemas import APIAuthParams, APITokenRequest, APIUserInfo
from app.id_base_model.schemas import CustomBaseModel, IntIDBaseModel, StrIDBaseModel


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


class StravaWebhookInput(CustomBaseModel):
    aspect_type: StravaAspectType
    object_id: int  # activity id or athelete id depending on object_type
    object_type: StravaObjectType
    owner_id: int  # athlete id


class StravaTokenRequest(APITokenRequest):
    client_id: int = settings.ENV_VARS.STRAVA_CLIENT_ID
    client_secret: str = settings.ENV_VARS.STRAVA_CLIENT_SECRET


class StravaDeauthorizeRequest:
    access_token: str


class StravaAthlete(IntIDBaseModel):
    username: str
    firstname: str
    lastname: str


class StravaAuth(APIUserInfo):
    pass


class StravaUserInfo(IntIDBaseModel, StravaAuth):
    user_id: int

    class Config:
        orm_mode = True


class StravaTokenResponse(StravaAuth):
    athlete: StravaAthlete


class StravaActivity(CustomBaseModel):
    id: int
    start_date: datetime
    description: Optional[str]


class StravaActivityStreamData(CustomBaseModel):
    data: list[float]


class StravaActivityStream(CustomBaseModel):
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

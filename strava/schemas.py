"""schemas for Strava"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from pydantic import BaseModel

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


class StravaAthlete(BaseModel):
    id: int
    username: str
    firstname: str
    lastname: str
    # TODO: what other attributes should i load in


class StravaOAuthTokenResponse(BaseModel):
    token_type: str
    expires_at: datetime
    expires_in: timedelta
    refresh_token: str
    access_token: str
    athlete: StravaAthlete

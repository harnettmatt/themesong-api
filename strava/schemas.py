"""schemas for Strava"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel


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

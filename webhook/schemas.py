"""schemas for Webhook"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class AspectType(Enum):
    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"


class ObjectType(Enum):
    ACTIVITY = "activity"
    ATHLETE = "athlete"


class WebhookInput(BaseModel):
    aspect_type: AspectType
    event_time: datetime
    object_id: int  # activity id or athelete id depending on object_type
    object_type: ObjectType
    owner_id: int  # athlete id
    subscription_id: int
    updates: Optional[dict] = None  # TODO: not sure if this is the right type


class WebhookVerifyInputHub(BaseModel):
    mode: str
    verify_token: str
    challenge: str


class WebhookVerifyInput(BaseModel):
    hub: WebhookVerifyInputHub

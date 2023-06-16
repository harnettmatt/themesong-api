from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from id_base_model.schemas import StrIDBaseModel
from settings import ENV_VARS


class SpotifyTokenRequest(BaseModel):
    redirect_uri: str = f"{ENV_VARS.HOST}/spotify/authorization"
    code: str
    grant_type: str = "authorization_code"


class SpotifyAuth(BaseModel):
    expires_in: int  # TODO: is there a clever way to type this as a time delta in seconds
    refresh_token: str
    access_token: str


class SpotifyTokenResponse(SpotifyAuth):
    pass


class SpotifyUserResponse(StrIDBaseModel):
    pass


class SpotifyRecentlyPlayedRequest(BaseModel):
    limit: int
    after: int


class SpotifyExternalUrls(BaseModel):
    spotify: str


class SpotifyTrack(BaseModel):
    id: str
    duration_ms: int
    name: str
    uri: str
    href: str  # link to the api to get more details on track
    external_urls: SpotifyExternalUrls


class SpotifyPlayHistoryObject(BaseModel):
    track: SpotifyTrack
    played_at: datetime


class SpotifyRecentlyPlayedResponse(BaseModel):
    next: Optional[str]
    items: List[SpotifyPlayHistoryObject]


class SpotifyUserInfo(StrIDBaseModel, SpotifyAuth):
    user_id: int

    class Config:
        orm_mode = True

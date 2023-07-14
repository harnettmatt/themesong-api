from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel, validator

from api_utils.schemas import APIAuthorizeParams, APITokenRequest, APIUserInfo
from id_base_model.schemas import StrIDBaseModel
from settings import ENV_VARS


class SpotifyTokenRequest(APITokenRequest):
    redirect_uri: Optional[str] = None

    @validator("redirect_uri", always=True)
    def validate_redirect_uri(cls, v, values):
        if values.get("code"):
            return f"{ENV_VARS.HOST}/spotify/authorization"
        return None


class SpotifyAuthStateParam(StrIDBaseModel):
    user_id: int


class SpotifyAuthorizeParams(APIAuthorizeParams):
    client_id: str = ENV_VARS.SPOTIFY_CLIENT_ID
    redirect_uri: str = f"{ENV_VARS.HOST}/spotify/authorization"
    scope: str = "user-read-private user-read-email user-read-recently-played"


class SpotifyAuth(APIUserInfo):
    expires_in: timedelta


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
    href: str  # link to the api to get more details on track


class SpotifyPlayHistoryObject(BaseModel):
    track: SpotifyTrack
    played_at: datetime


class SpotifyRecentlyPlayedResponse(BaseModel):
    next: Optional[str]
    items: List[SpotifyPlayHistoryObject]

    def get_spotify_track_for_datetime(
        self, max_hr_date_time: datetime
    ) -> Optional[SpotifyTrack]:
        self.items.reverse()
        for play_history_item in self.items:
            end_time = play_history_item.played_at
            start_time = end_time - timedelta(
                milliseconds=play_history_item.track.duration_ms
            )
            # max_hr_date_time falls within track time
            if start_time <= max_hr_date_time and max_hr_date_time <= end_time:
                return play_history_item.track
            # max_hr_date_time is later than the track
            elif start_time < max_hr_date_time and end_time < max_hr_date_time:
                continue
            # max_hr_date_time is earlier than the track
            else:
                raise Exception("Didn't search for tracks far enough back in time")

        return None


class SpotifyUserInfo(StrIDBaseModel, SpotifyAuth):
    user_id: int

    class Config:
        orm_mode = True

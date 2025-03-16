from datetime import datetime, timedelta
from typing import List, Optional
from urllib.parse import urlencode

from pydantic import validator

from app import settings
from app.api_utils.schemas import (
    APIAuthParams,
    APITokenRequest,
    APIUserInfo,
    RequestGrantType,
)
from app.id_base_model.schemas import CustomBaseModel, StrIDBaseModel


class SpotifyRefreshTokenRequest(APITokenRequest):
    refresh_token: str
    grant_type: RequestGrantType = RequestGrantType.REFRESH_TOKEN
    client_id: str = settings.ENV_VARS.SPOTIFY_CLIENT_ID
    client_secret: str = settings.ENV_VARS.SPOTIFY_CLIENT_SECRET


class SpotifyTokenRequest(APITokenRequest):
    redirect_uri: Optional[str] = None

    @validator("redirect_uri", always=True)
    def validate_redirect_uri(cls, v, values):
        if values.get("code"):
            return f"{settings.ENV_VARS.HOST}/spotify/authorization"
        return None


class SpotifyAuthStateParam(StrIDBaseModel):
    user_id: int


class SpotifyAuthParams(APIAuthParams):
    client_id: str = settings.ENV_VARS.SPOTIFY_CLIENT_ID
    redirect_uri: str = f"{settings.ENV_VARS.HOST}/spotify/authorization"
    scope: str = "user-read-private user-read-email user-read-recently-played"

    def format_as_url(self) -> str:
        return f"https://accounts.spotify.com/authorize?{urlencode((self.dict()))}"


class SpotifyAuth(APIUserInfo):
    pass


class SpotifyTokenResponse(SpotifyAuth):
    pass


class SpotifyUserResponse(StrIDBaseModel):
    pass


class SpotifyRecentlyPlayedRequest(CustomBaseModel):
    limit: int
    after: int


class SpotifyExternalUrls(CustomBaseModel):
    spotify: str


class SpotifyTrack(CustomBaseModel):
    id: str
    duration_ms: int
    name: str
    href: str  # link to the api to get more details on track


class SpotifyPlayHistoryObject(CustomBaseModel):
    track: SpotifyTrack
    played_at: datetime


class SpotifyRecentlyPlayedResponse(CustomBaseModel):
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
            # max_hr_date_time is earlier than the tracks returned - spofity only returns 50 tracks :(
            else:
                pass

        return None


class SpotifyUserInfo(StrIDBaseModel, SpotifyAuth):
    user_id: int

    class Config:
        orm_mode = True

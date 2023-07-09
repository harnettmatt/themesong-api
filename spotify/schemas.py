from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel

from api_utils.schemas import APIUserInfo, RequestGrantType
from id_base_model.schemas import StrIDBaseModel


class SpotifyTokenRequest(BaseModel):
    grant_type: RequestGrantType
    # TODO: set this based on the code and refresh token
    redirect_uri: Optional[str] = None
    refresh_token: Optional[str] = None
    code: Optional[str] = None


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
    uri: str
    href: str  # link to the api to get more details on track
    external_urls: SpotifyExternalUrls


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

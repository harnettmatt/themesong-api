from datetime import datetime, timedelta
from typing import Optional

from app.spotify import schemas
from app.spotify.client import SpotifyAPIService


class SpotifyService:
    api: SpotifyAPIService

    def __init__(self, api: SpotifyAPIService) -> None:
        self.api = api

    def get_track_for_datetime(
        self, max_hr_date_time: datetime
    ) -> Optional[schemas.SpotifyTrack]:
        user_history = self.api.get_recenty_played(
            after=max_hr_date_time - timedelta(minutes=30)  # type: ignore
        )
        return user_history.get_spotify_track_for_datetime(
            max_hr_date_time=max_hr_date_time
        )

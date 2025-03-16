from datetime import datetime
from typing import Optional, Tuple

from app.spotify.schemas import SpotifyTrack
from app.strava import schemas
from app.strava.client import StravaAPIService


class StravaService:
    api: StravaAPIService

    def __init__(self, api: StravaAPIService) -> None:
        self.api = api

    def get_max_hr_date_time_for_activity(
        self, activity: schemas.StravaActivity
    ) -> Tuple[Optional[datetime], Optional[float]]:
        activity_stream = self.api.get_stream_for_activity(
            id=activity.id,
            stream_keys=[
                schemas.StravaStreamKeys.TIME,
                schemas.StravaStreamKeys.HEARTRATE,
            ],
        )
        max_hr_time_mark, max_heart_rate = activity_stream.get_max_heartrate_time_mark()
        if max_hr_time_mark is None:
            return None, None

        heart_rate_time = activity.start_date + max_hr_time_mark

        return heart_rate_time, max_heart_rate

    def update_activity_with_track(
        self,
        activity: schemas.StravaActivity,
        track: Optional[SpotifyTrack],
        max_hr: Optional[float],
    ):
        if activity.description and "Theme Song:" in activity.description:
            return

        # TODO: track.href is None in some scenarios? - need to figure out why its None and then handle it, if None is a valid value
        theme_song_string = (
            f"Theme Song: {track.name} - {track.href}, Max HR: {max_hr} bpm"
            if track is not None
            else "Theme Song: sweet sounds of silence"
        )
        if activity.description:
            description = f"{activity.description} \n{theme_song_string}"
        else:
            description = theme_song_string

        self.api.update_activity(
            id=activity.id,
            data={"description": description},
        )

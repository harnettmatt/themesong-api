from datetime import datetime
from typing import Optional

from app.spotify.schemas import SpotifyTrack
from app.strava import schemas
from app.strava.client import StravaAPIService


class StravaService:
    api: StravaAPIService

    def __init__(self, api: StravaAPIService) -> None:
        self.api = api

    def get_max_hr_date_time_for_activity(
        self, activity: schemas.StravaActivity
    ) -> Optional[datetime]:
        activity_stream = self.api.get_stream_for_activity(
            id=activity.id,
            stream_keys=[
                schemas.StravaStreamKeys.TIME,
                schemas.StravaStreamKeys.HEARTRATE,
            ],
        )
        max_hr_time_mark = activity_stream.get_max_heartrate_time_mark()
        if max_hr_time_mark is None:
            return None

        return activity.start_date + max_hr_time_mark

    def update_activity_with_track(
        self, activity: schemas.StravaActivity, track: SpotifyTrack
    ):
        if activity.description and "Theme Song:" in activity.description:
            return

        # TODO: track.href is None in some scenarios? - need to figure out why its None and then handle it, if None is a valid value
        theme_song_string = f"Theme Song: {track.name} - {track.href}"
        if activity.description:
            description = f"{activity.description} \n{theme_song_string}"
        else:
            description = theme_song_string

        self.api.update_activity(
            id=activity.id,
            data={"description": description},
        )

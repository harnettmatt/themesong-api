from datetime import datetime
from typing import Optional

from spotify.schemas import SpotifyTrack
from strava import schemas
from strava.client import StravaAPIService


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
        # TODO: add logic to cherck existing description to see if it already contains the track
        self.api.update_activity(
            id=activity.id,
            data={
                "description": f"{activity.description} \nTheme Song: {track.name} - {track.href}"
            },
        )

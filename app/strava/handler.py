import logging
from typing import Optional

from fastapi import HTTPException

from app.database.service import DatabaseService
from app.spotify.schemas import SpotifyTrack, SpotifyUserInfo
from app.spotify.service import SpotifyAPIService, SpotifyService
from app.strava import schemas
from app.strava.client import StravaAPIService
from app.strava.service import StravaService
from app.user.models import User


class StravaWebhookHandler:
    event: schemas.StravaWebhookInput
    db_service: DatabaseService

    def __init__(
        self, event: schemas.StravaWebhookInput, db_service: DatabaseService
    ) -> None:
        self.event = event
        self.db_service = db_service

    def handle(self) -> Optional[SpotifyTrack]:
        if self.event.object_type != schemas.StravaObjectType.ACTIVITY:
            return None
        if self.event.aspect_type == schemas.StravaAspectType.CREATE:
            return self._handle_activity_create()
        return None

    def _handle_activity_create(self) -> Optional[SpotifyTrack]:
        # get user
        user = self.db_service.get(id=self.event.owner_id, model_type=User)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # setup services
        strava_api_service = StravaAPIService(
            schemas.StravaUserInfo.from_orm(user.strava_user_info),
            db_service=self.db_service,
        )
        strava_service = StravaService(api=strava_api_service)
        spotify_api_service = SpotifyAPIService(
            user_info=SpotifyUserInfo.from_orm(user.spotify_user_info),
            db_service=self.db_service,
        )
        spotify_service = SpotifyService(api=spotify_api_service)

        # get activity and max hr
        activity = strava_service.api.get_activity(self.event.object_id)
        max_hr_date_time = strava_service.get_max_hr_date_time_for_activity(activity)
        if max_hr_date_time is None:
            logging.info(
                f"Could not find a max heart rate for the following activity: {activity.json()}"
            )

        # get track if hr data exists
        track = (
            spotify_service.get_track_for_datetime(max_hr_date_time)
            if max_hr_date_time
            else None
        )
        if track is None:
            logging.info(
                f"Could not find a track for the following datetime: {max_hr_date_time}"
            )

        # update activity
        strava_service.update_activity_with_track(activity, track)

        return track

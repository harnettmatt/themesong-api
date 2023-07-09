from database.database_service import DatabaseService
from spotify.schemas import SpotifyUserInfo
from spotify.service import SpotifyAPIService, SpotifyService
from strava import schemas
from strava.client import StravaAPIService
from strava.service import StravaService
from user.models import User


class StravaWebhookHandler:
    event: schemas.StravaWebhookInput
    db_service: DatabaseService

    def __init__(
        self, event: schemas.StravaWebhookInput, db_service: DatabaseService
    ) -> None:
        self.event = event
        self.db_service = db_service

    def handle(self):
        if self.event.object_type != schemas.StravaObjectType.ACTIVITY:
            print("object type not supported")
            return
        if (
            self.event.aspect_type == schemas.StravaAspectType.UPDATE
            or self.event.aspect_type == schemas.StravaAspectType.CREATE
        ):
            return self._handle_activity_update_and_create()
        print("aspect type not supported")

    def _handle_activity_update_and_create(self):
        # get user
        user = self.db_service.get(id=self.event.owner_id, model_type=User)

        # setup services
        strava_api_service = StravaAPIService(
            schemas.StravaUserInfo.from_orm(user.strava_info),
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
            print("could not find max hr")
            return

        # get track
        track = spotify_service.get_track_for_datetime(max_hr_date_time)
        if track is None:
            print("could not find track")
            return

        # update activity
        strava_service.update_activity_with_track(activity, track)
        # TODO: do i need to return something here. Check Strava docs if this doesn't work as is

from datetime import datetime
from enum import Enum
from typing import List, Optional

import requests
from requests import Response

from api_utils.service import APIService
from database.database_service import DatabaseService
from spotify.schemas import SpotifyTrack
from strava import models, schemas

STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STAVA_API_PREFIX = "https://www.strava.com/api/v3"


class StreamKeys(Enum):
    TIME = "time"
    HEARTRATE = "heartrate"


class StravaAPIService(APIService):
    user_info: schemas.StravaUserInfo

    def __init__(
        self, user_info: schemas.StravaUserInfo, db_service: DatabaseService
    ) -> None:
        super().__init__(user_info=user_info, db_service=db_service)

    def check_auth(self):
        if self.user_info.expires_at > datetime.now():
            return
        new_auth = self.refresh_token()
        self.user_info = schemas.StravaUserInfo(
            **new_auth.dict(), **self.user_info.dict()
        )
        # TODO: do we need to make sure that in memory and db are in sync?
        self.db_service.update(
            id=self.user_info.id,
            input_schema=self.user_info,
            model_type=models.StravaUserInfo,
        )

    @staticmethod
    def exchange_code(code: str) -> schemas.StravaOAuthTokenResponse:
        response: Response = requests.post(
            STRAVA_TOKEN_URL,
            params=schemas.StravaOAuthTokenRequest(
                grant_type=schemas.RequestGrantType.AUTHORIZATION_CODE,
                code=code,
            ).dict(),
        )
        return schemas.StravaOAuthTokenResponse(**response.json())

    def refresh_token(self) -> schemas.StravaAuth:
        response: Response = requests.post(
            STRAVA_TOKEN_URL,
            params=schemas.StravaOAuthTokenRequest(
                grant_type=schemas.RequestGrantType.REFRESH_TOKEN,
                refresh_token=self.user_info.refresh_token,
            ).dict(),
        )
        return schemas.StravaAuth(**response.json())

    def _execute(
        self, func, url: str, params: Optional[dict] = None, data: Optional[dict] = None
    ) -> Response:
        self.check_auth()
        response: Response = func(
            url,
            headers={"Authorization": f"Bearer {self.user_info.access_token}"},
            params=params,
            data=data,
        )
        return response

    def get_activity(self, id: int) -> schemas.StravaActivity:
        response = self._execute(requests.get, f"{STAVA_API_PREFIX}/activities/{id}")
        return schemas.StravaActivity(**response.json())

    def get_stream_for_activity(
        self, id: int, stream_keys: List[StreamKeys], key_by_type: bool = True
    ) -> schemas.StravaActivityStream:
        stream_keys_str = ",".join([key.value for key in stream_keys])
        response = self._execute(
            requests.get,
            f"{STAVA_API_PREFIX}/activities/{id}/streams",
            params={"keys": stream_keys_str, "key_by_type": str(key_by_type).lower()},
        )
        return schemas.StravaActivityStream(**response.json())

    def update_activity(self, id: int, data: dict):
        self._execute(
            requests.put,
            f"{STAVA_API_PREFIX}/activities/{id}",
            data=data,
        )


class StravaService:
    api: StravaAPIService

    def __init__(self, api: StravaAPIService) -> None:
        self.api = api

    def get_max_hr_date_time_for_activity(
        self, activity: schemas.StravaActivity
    ) -> Optional[datetime]:
        activity_stream = self.api.get_stream_for_activity(
            id=activity.id, stream_keys=[StreamKeys.TIME, StreamKeys.HEARTRATE]
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

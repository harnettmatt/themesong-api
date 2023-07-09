import base64
from datetime import datetime, timedelta
from typing import Optional

import requests
from requests import Response

from api_utils.service import APIService
from database.database_service import DatabaseService
from settings import ENV_VARS
from spotify import schemas

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_BASE_URL = "https://api.spotify.com/v1"


class SpotifyAPIService(APIService):
    user_info: schemas.SpotifyUserInfo

    def __init__(
        self, user_info: schemas.SpotifyUserInfo, db_service: DatabaseService
    ) -> None:
        super().__init__(user_info=user_info, db_service=db_service)

    def check_auth(self):
        expires_at = datetime.utcnow() + self.user_info.expires_in
        if expires_at > datetime.now():
            return
        new_auth = self.refresh_token()
        self.user_info = schemas.SpotifyUserInfo(
            **new_auth.dict(), **self.user_info.dict()
        )

    def refresh_token(self) -> schemas.SpotifyAuth:
        response: Response = requests.post(
            SPOTIFY_TOKEN_URL,
            data=schemas.SpotifyTokenRequest(
                grant_type=schemas.RequestGrantType.REFRESH_TOKEN,
                refresh_token=self.user_info.refresh_token,
            ).dict(),
            headers={"Authorization": f"Basic {self.get_encoded_token()}"},
        )
        return schemas.SpotifyAuth(**response.json())

    @staticmethod
    def get_encoded_token() -> str:
        token = f"{ENV_VARS.SPOTIFY_CLIENT_ID}:{ENV_VARS.SPOTIFY_CLIENT_SECRET}"
        return base64.b64encode(token.encode("ascii")).decode("ascii")

    @classmethod
    def exchange_code(cls, code: str) -> schemas.SpotifyTokenResponse:
        response: Response = requests.post(
            SPOTIFY_TOKEN_URL,
            data=schemas.SpotifyTokenRequest(
                grant_type=schemas.RequestGrantType.AUTHORIZATION_CODE,
                redirect_uri=f"{ENV_VARS.HOST}/spotify/authorization",
                code=code,
            ).dict(),
            headers={"Authorization": f"Basic {cls.get_encoded_token()}"},
        )

        return schemas.SpotifyTokenResponse(**response.json())

    def get_user(self) -> schemas.SpotifyUserResponse:
        response: Response = self._execute(requests.get, f"{SPOTIFY_BASE_URL}/me")
        return schemas.SpotifyUserResponse(**response.json())

    def get_user_history(
        self, after: datetime, limit: int = 50
    ) -> schemas.SpotifyRecentlyPlayedResponse:
        after_milliseconds = int(after.timestamp() * 1000)
        response: Response = self._execute(
            requests.get,
            f"{SPOTIFY_BASE_URL}/me/player/recently-played",
            params=schemas.SpotifyRecentlyPlayedRequest(
                after=after_milliseconds, limit=limit
            ).dict(),
        )
        return schemas.SpotifyRecentlyPlayedResponse(**response.json())


class SpotifyService:
    api: SpotifyAPIService

    def __init__(self, api: SpotifyAPIService) -> None:
        self.api = api

    def get_track_for_datetime(
        self, max_hr_date_time: datetime
    ) -> Optional[schemas.SpotifyTrack]:
        user_history = self.api.get_user_history(
            after=max_hr_date_time - timedelta(minutes=30)  # type: ignore
        )
        return user_history.get_spotify_track_for_datetime(
            max_hr_date_time=max_hr_date_time
        )

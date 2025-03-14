import base64
import logging
from datetime import datetime, timedelta, timezone

import requests
from requests import Response

from app import settings
from app.api_utils.schemas import RequestGrantType
from app.api_utils.service import APIService
from app.database.service import DatabaseService
from app.spotify import models, schemas

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_BASE_URL = "https://api.spotify.com/v1"


class SpotifyAPIService(APIService):
    user_info: schemas.SpotifyUserInfo

    def __init__(
        self, user_info: schemas.SpotifyUserInfo, db_service: DatabaseService
    ) -> None:
        super().__init__(user_info=user_info, db_service=db_service)

    def check_auth(self):
        if self.user_info.expires_at > datetime.now(timezone.utc):
            return
        new_auth = self.refresh_token()
        new_user_info_data = self.user_info.dict() | new_auth.dict()
        self.user_info = schemas.SpotifyUserInfo(**new_user_info_data)

        # TODO: do we need to make sure that in memory and db are in sync?
        self.db_service.update(
            id=self.user_info.id,
            input_schema=self.user_info,
            model_type=models.SpotifyUserInfo,
        )

    def refresh_token(self) -> schemas.SpotifyAuth:
        logging.info(f"Refreshing Spotify token for user: {self.user_info.id}")
        request_body = schemas.SpotifyTokenRequest(
            grant_type="refresh_token",
            refresh_token=self.user_info.refresh_token,
        )
        response = self._execute(
            requests.post,
            SPOTIFY_TOKEN_URL,
            data=request_body.dict(exclude_none=True),
            # headers={"Authorization": f"Basic {self.get_encoded_token()}"},
        )
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=response.json().get("expires_in")
        )
        return schemas.SpotifyAuth(
            **response.json(),
            refresh_token=self.user_info.refresh_token,
            expires_at=expires_at,
        )

    @staticmethod
    def get_encoded_token() -> str:
        token = f"{settings.ENV_VARS.SPOTIFY_CLIENT_ID}:{settings.ENV_VARS.SPOTIFY_CLIENT_SECRET}"
        return base64.b64encode(token.encode("ascii")).decode("ascii")

    @classmethod
    def exchange_code(cls, code: str) -> schemas.SpotifyTokenResponse:
        request_body = schemas.SpotifyTokenRequest(
            grant_type=RequestGrantType.AUTHORIZATION_CODE,
            redirect_uri=f"{settings.ENV_VARS.HOST}/spotify/authorization",
            code=code,
        )
        response = cls._execute(
            requests.post,
            SPOTIFY_TOKEN_URL,
            data=request_body.dict(),
            headers={"Authorization": f"Basic {cls.get_encoded_token()}"},
        )
        # TODO: expires_at should be a function. maybe this is a property of some kind on SpotifyTokenResponse?
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=response.json().get("expires_in")
        )
        return schemas.SpotifyTokenResponse(**response.json(), expires_at=expires_at)

    # if we use this function somewhere else it will need to be refactored to have refresh token logic
    @classmethod
    def get_user(cls, access_token: str) -> schemas.SpotifyUserResponse:
        response = cls._execute(
            requests.get,
            f"{SPOTIFY_BASE_URL}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return schemas.SpotifyUserResponse(**response.json())

    def get_recenty_played(
        self, after: datetime, limit: int = 50
    ) -> schemas.SpotifyRecentlyPlayedResponse:
        after_milliseconds = int(after.timestamp() * 1000)
        response: Response = self._execute_with_auth(
            requests.get,
            f"{SPOTIFY_BASE_URL}/me/player/recently-played",
            params=schemas.SpotifyRecentlyPlayedRequest(
                after=after_milliseconds, limit=limit
            ).dict(),
        )
        return schemas.SpotifyRecentlyPlayedResponse(**response.json())

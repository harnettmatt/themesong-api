import base64
from datetime import datetime

import requests
from requests import Response

from database.database_service import DatabaseService
from settings import ENV_VARS
from spotify import models, schemas

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_BASE_URL = "https://api.spotify.com/v1"


class SpotifyUserInfoService:
    db_service: DatabaseService

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def merge(self, spotify_user_info: schemas.SpotifyUserInfo):
        self.db_service.merge(
            input_schema=spotify_user_info, model_type=models.SpotifyUserInfo
        )


class SpotifyAPIService:
    token: str

    def __init__(self, token) -> None:
        self.token = token

    @staticmethod
    def exchange_code(code: str) -> schemas.SpotifyTokenResponse:
        token = f"{ENV_VARS.SPOTIFY_CLIENT_ID}:{ENV_VARS.SPOTIFY_CLIENT_SECRET}"
        encoded_token = base64.b64encode(token.encode("ascii")).decode("ascii")
        response: Response = requests.post(
            SPOTIFY_TOKEN_URL,
            data=schemas.SpotifyTokenRequest(code=code).dict(),
            headers={"Authorization": f"Basic {encoded_token}"},
        )

        return schemas.SpotifyTokenResponse(**response.json())

    def get_user(self) -> schemas.SpotifyUserResponse:
        response: Response = requests.get(
            f"{SPOTIFY_BASE_URL}/me",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        return schemas.SpotifyUserResponse(**response.json())

    def get_user_history(
        self, after: datetime, limit: int = 50
    ) -> schemas.SpotifyRecentlyPlayedResponse:
        after_milliseconds = int(after.timestamp() * 1000)
        response: Response = requests.get(
            f"{SPOTIFY_BASE_URL}/me/player/recently-played",
            headers={"Authorization": f"Bearer {self.token}"},
            params=schemas.SpotifyRecentlyPlayedRequest(
                after=after_milliseconds, limit=limit
            ).dict(),
        )
        print(response.json())
        return schemas.SpotifyRecentlyPlayedResponse(**response.json())

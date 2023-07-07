from enum import Enum
from typing import List

import requests
from requests import Response

from strava import schemas

STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STAVA_API_PREFIX = "https://www.strava.com/api/v3"


class StreamKeys(Enum):
    TIME = "time"
    HEARTRATE = "heartrate"


class StravaAPIService:
    token: str

    def __init__(self, token) -> None:
        self.token = token

    @staticmethod
    def exchange_code(code: str) -> schemas.StravaOAuthTokenResponse:
        response: Response = requests.post(
            STRAVA_TOKEN_URL,
            params=schemas.StravaOAuthTokenRequest(code=code).dict(),
        )
        return schemas.StravaOAuthTokenResponse(**response.json())

    def get_activity(self, id: int):
        response: Response = requests.get(
            f"{STAVA_API_PREFIX}/activities/{id}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        return schemas.StravaActivity(**response.json())

    def get_stream_for_activity(
        self, id: int, stream_keys: List[StreamKeys], key_by_type: bool = True
    ):
        stream_keys_str = ",".join([key.value for key in stream_keys])
        response = requests.get(
            f"{STAVA_API_PREFIX}/activities/{id}/streams?&keys={stream_keys_str}&key_by_type={str(key_by_type).lower()}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        # TODO: type this response
        return response.json()

    def update_activity(self, id: int, data: dict):
        requests.put(
            f"{STAVA_API_PREFIX}/activities/{id}",
            headers={"Authorization": f"Bearer {self.token}"},
            data=data,
        )

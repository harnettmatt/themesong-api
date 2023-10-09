from datetime import datetime, timezone
from typing import List

import requests
from requests import Response

from app.api_utils.service import APIService
from app.database.service import DatabaseService
from app.strava import models, schemas

TOKEN_URL = "https://www.strava.com/oauth/token"
API_PREFIX = "https://www.strava.com/api/v3"


class StravaAPIService(APIService):
    user_info: schemas.StravaUserInfo

    def __init__(
        self, user_info: schemas.StravaUserInfo, db_service: DatabaseService
    ) -> None:
        super().__init__(user_info=user_info, db_service=db_service)

    def check_auth(self):
        if self.user_info.expires_at > datetime.now(timezone.utc):
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

    @classmethod
    def exchange_code(cls, code: str) -> schemas.StravaTokenResponse:
        params = schemas.StravaTokenRequest(code=code)
        response: Response = cls._execute(
            requests.post,
            TOKEN_URL,
            params=params.dict(),
        )
        return schemas.StravaTokenResponse(**response.json())

    def refresh_token(self) -> schemas.StravaAuth:
        params = schemas.StravaTokenRequest(refresh_token=self.user_info.refresh_token)
        response = self._execute_with_auth(
            requests.post, TOKEN_URL, params=params.dict()
        )
        return schemas.StravaAuth(**response.json())

    def get_activity(self, id: int) -> schemas.StravaActivity:
        response = self._execute_with_auth(
            requests.get, f"{API_PREFIX}/activities/{id}"
        )
        return schemas.StravaActivity(**response.json())

    def get_stream_for_activity(
        self,
        id: int,
        stream_keys: List[schemas.StravaStreamKeys],
        key_by_type: bool = True,
    ) -> schemas.StravaActivityStream:
        stream_keys_str = ",".join([key.value for key in stream_keys])
        response = self._execute_with_auth(
            requests.get,
            f"{API_PREFIX}/activities/{id}/streams",
            params={"keys": stream_keys_str, "key_by_type": str(key_by_type).lower()},
        )
        return schemas.StravaActivityStream(**response.json())

    def update_activity(self, id: int, data: dict):
        self._execute_with_auth(
            requests.put,
            f"{API_PREFIX}/activities/{id}",
            data=data,
        )

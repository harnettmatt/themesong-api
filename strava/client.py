from datetime import datetime
from typing import List, Optional

import requests
from requests import Response

from api_utils.service import APIService
from database.database_service import DatabaseService
from strava import models, schemas

STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STAVA_API_PREFIX = "https://www.strava.com/api/v3"


class StravaAPIService(APIService):
    user_info: schemas.StravaUserInfo

    def __init__(
        self, user_info: schemas.StravaUserInfo, db_service: DatabaseService
    ) -> None:
        super().__init__(user_info=user_info, db_service=db_service)

    def check_auth(self):
        if self.user_info.expires_at > datetime.utcnow():
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
        self,
        id: int,
        stream_keys: List[schemas.StravaStreamKeys],
        key_by_type: bool = True,
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

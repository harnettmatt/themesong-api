from abc import abstractmethod
from typing import Optional

from requests import Response

from api_utils.schemas import APIUserInfo
from database.service import DatabaseService


class APIService:
    user_info: APIUserInfo
    db_service: DatabaseService

    def __init__(self, user_info: APIUserInfo, db_service: DatabaseService) -> None:
        self.user_info = user_info
        self.db_service = db_service

    @abstractmethod
    def check_auth(self):
        raise NotImplementedError

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

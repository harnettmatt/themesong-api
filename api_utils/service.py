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

    @staticmethod
    def _execute(
        func,
        url: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> Response:
        response: Response = func(url, headers=headers, params=params, data=data)
        response.raise_for_status()
        return response

    def _execute_with_auth(
        self,
        func,
        url: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> Response:
        self.check_auth()
        if headers and not headers.get("Authorization"):
            headers["Authorization"] = f"Bearer {self.user_info.access_token}"
        return self._execute(
            func=func, url=url, params=params, data=data, headers=headers
        )

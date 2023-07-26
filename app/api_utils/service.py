from abc import abstractmethod
from typing import Optional, Type, TypeVar

from fastapi import HTTPException
from requests import Response

from app.api_utils.schemas import APIUserInfo
from app.database.service import DatabaseService
from app.persistable.models import Persistable

P = TypeVar("P", bound=Persistable)


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

    @staticmethod
    def authorize_redirect_state(
        state: str, model_type: Type[P], db_service: DatabaseService
    ) -> P:
        auth_state_param = db_service.get(id=state, model_type=model_type)
        if auth_state_param is None:
            raise HTTPException(status_code=403, detail="Access Denied")
        db_service.delete_instance(model=auth_state_param)
        return auth_state_param

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

from pydantic import BaseModel


class APIUserInfo(BaseModel):
    access_token: str
    refresh_token: str

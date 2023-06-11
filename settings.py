from dotenv import dotenv_values
from pydantic import BaseModel


class EnvironmentVariables(BaseModel):
    STRAVA_CLIENT_ID: int
    STRAVA_CLIENT_SECRET: str
    STRAVA_WEBHOOK_TOKEN: str


ENV_VARS = EnvironmentVariables(**dotenv_values(".env"))  # type: ignore

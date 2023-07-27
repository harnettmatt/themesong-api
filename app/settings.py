from pydantic import BaseSettings


class EnvironmentVariables(BaseSettings):
    HOST: str

    STRAVA_CLIENT_ID: int
    STRAVA_CLIENT_SECRET: str
    STRAVA_WEBHOOK_TOKEN: str

    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str

    DB_HOST: str
    DB_NAME: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str

    class Config:
        case_sensitive = True


ENV_VARS = EnvironmentVariables()  # type: ignore

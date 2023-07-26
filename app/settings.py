from pydantic import BaseSettings


class EnvironmentVariables(BaseSettings):
    HOST: str

    STRAVA_CLIENT_ID: int
    STRAVA_CLIENT_SECRET: str
    STRAVA_WEBHOOK_TOKEN: str

    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str

    class Config:
        env_file = ".env"
        case_sensitive = True


ENV_VARS = EnvironmentVariables()  # type: ignore

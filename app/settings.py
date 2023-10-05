from pydantic import BaseSettings


class EnvironmentVariables(BaseSettings):
    # default values are for starting locally
    # specify .env file to adjust values
    HOST: str
    FE_HOST: str

    STRAVA_CLIENT_ID: int
    STRAVA_CLIENT_SECRET: str
    STRAVA_WEBHOOK_TOKEN: str

    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str

    DB_HOST: str = "localhost"
    DB_NAME: str = "postgres"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    class Config:
        case_sensitive = True


ENV_VARS = EnvironmentVariables()  # type: ignore

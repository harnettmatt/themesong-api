from pydantic import BaseSettings


class EnvironmentVariables(BaseSettings):
    # default values are for starting locally
    # specify .env file to adjust values

    HOST: str  # ngrox url or public url for API (used for 3rd party API redirects)
    FE_HOST: str

    # Credentials for Strava API are different for dev and prod
    STRAVA_CLIENT_ID: int
    STRAVA_CLIENT_SECRET: str
    STRAVA_WEBHOOK_TOKEN: str  # TODO: this webhook token keeps regenerating on strava's end - Figure out handle this properly

    # Credentials for Spotify API are the same between dev and prod
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str

    DB_HOST: str = "localhost"
    DB_NAME: str = "postgres"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    LOG_LEVEL: str = "WARNING"

    class Config:
        case_sensitive = True


ENV_VARS = EnvironmentVariables()  # type: ignore

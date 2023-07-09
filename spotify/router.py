"""Routing handler for /spotify"""
from typing import Optional

from fastapi import APIRouter, Depends

from database.database import get_db_service
from database.database_service import DatabaseService
from spotify import models, schemas
from spotify.client import SpotifyAPIService

ROUTER = APIRouter()


@ROUTER.get("/authorization", status_code=200)
def authorization(
    code: str,
    state: Optional[str],
    db_service: DatabaseService = Depends(get_db_service),
):
    """
    Redirect handler for when a Spotify user grants access to the application
    Handler is responsible for:
        - swapping token for bearer and refresh
        - persisting relevant user information to the db

    # TODO: add state code to url for security
    Auth url: https://accounts.spotify.com/authorize?response_type=code&client_id=1da7b7b76bcf4da2b2e058dbf33a7117&scope=user-read-private%20user-read-email%20user-read-recently-played&redirect_uri=https://17dd-65-154-225-130.ngrok-free.app/spotify/authorization&state=
      client_id: client_id,
      scope: scope,
      redirect_uri: redirect_uri,
      state: state
    }));
    """
    token_response = SpotifyAPIService.exchange_code(code)
    user_response = SpotifyAPIService.get_user(token_response.access_token)

    # TODO: need to figure out how to get user id here. Hardcoding for now
    #       maybe its None at the start and then associated later?
    #       maybe the creation of the userinfo object needs to happen in a separate request from the client
    spotify_user_info = schemas.SpotifyUserInfo(
        user_id=42496487,
        **token_response.dict(),
        **user_response.dict(),
    )
    db_service.merge(input_schema=spotify_user_info, model_type=models.SpotifyUserInfo)

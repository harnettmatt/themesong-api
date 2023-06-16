"""Routing handler for /spotify"""
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_session
from database.database_service import DatabaseService
from spotify.schemas import SpotifyUserInfo
from spotify.service import SpotifyAPIService, SpotifyUserInfoService

ROUTER = APIRouter()


@ROUTER.get("/authorization", status_code=200)
def authorization(
    code: str, state: Optional[str], session: Session = Depends(get_session)
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
    # TODO: services like SpotifyAPIService, DatabaseService, and SpotifyUserInfoService should probably be be dependencies
    spotify_api_service = SpotifyAPIService()
    token_response = spotify_api_service.exchange_code_for_token(code)
    user_response = spotify_api_service.get_user(token_response.access_token)

    # TODO: need to figure out how to get user id here. Hardcoding for now
    #       maybe its None at the start and then associated later?
    #       maybe the creation of the userinfo object needs to happen in a separate request from the client
    spotify_user_info = SpotifyUserInfo(
        user_id=42496487,
        **token_response.dict(),
        **user_response.dict(),
    )
    SpotifyUserInfoService(db_service=DatabaseService(session)).merge(spotify_user_info)

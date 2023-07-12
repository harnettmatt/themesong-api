"""Routing handler for /spotify"""
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from database.database import get_db_service
from database.service import DatabaseService
from spotify import models, schemas
from spotify.client import SpotifyAPIService

ROUTER = APIRouter()


@ROUTER.get("/login")
def login(
    user_id: str,
    db_service: DatabaseService = Depends(get_db_service),
):
    """
    TODO: replace user id with some oauth token
    Endpoint for logging in a user
    """
    authorize_params = schemas.SpotifyAuthorizeParams()
    # TODO: create dict with user id and generated uuid, persist, encode and pass in to url as states
    return RedirectResponse(
        url=f"https://accounts.spotify.com/authorize?{urlencode(authorize_params.dict())}"
    )


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
    """
    # TODO: decode state code and check against db
    token_response = SpotifyAPIService.exchange_code(code)
    user_response = SpotifyAPIService.get_user(token_response.access_token)

    # TODO: get user_id from state code
    spotify_user_info = schemas.SpotifyUserInfo(
        user_id=42496487,
        **token_response.dict(),
        **user_response.dict(),
    )
    db_service.merge(input_schema=spotify_user_info, model_type=models.SpotifyUserInfo)

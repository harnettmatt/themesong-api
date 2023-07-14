"""Routing handler for /spotify"""
import random
import string
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse

from database.database import get_db_service
from database.service import DatabaseService
from spotify import models, schemas
from spotify.client import SpotifyAPIService

ROUTER = APIRouter()


@ROUTER.get("/login")
def login(
    user_id: int,
    db_service: DatabaseService = Depends(get_db_service),
):
    """
    TODO: replace user id with some oauth token
    Endpoint for logging in a user
    """
    state = "".join(random.choices(string.ascii_letters, k=16))
    db_service.create(
        schemas.SpotifyAuthStateParam(id=state, user_id=user_id),
        models.SpotifyAuthStateParam,
    )
    authorize_params = schemas.SpotifyAuthorizeParams(state=state)

    return RedirectResponse(
        url=f"https://accounts.spotify.com/authorize?{urlencode(authorize_params.dict())}"
    )


@ROUTER.get("/authorization", status_code=200)
def authorization(
    code: str,
    state: str,
    db_service: DatabaseService = Depends(get_db_service),
):
    """
    Redirect handler for when a Spotify user grants access to the application
    Handler is responsible for:
        - swapping token for bearer and refresh
        - persisting relevant user information to the db
    """
    auth_state_param = db_service.get(id=state, model_type=models.SpotifyAuthStateParam)
    if auth_state_param is None:
        raise HTTPException(status_code=403, detail="Access Denied")
    user_id = auth_state_param.user_id
    db_service.delete_instance(model=auth_state_param)

    token_response = SpotifyAPIService.exchange_code(code)
    user_response = SpotifyAPIService.get_user(token_response.access_token)

    spotify_user_info = schemas.SpotifyUserInfo(
        user_id=user_id,
        **token_response.dict(),
        **user_response.dict(),
    )
    db_service.merge(input_schema=spotify_user_info, model_type=models.SpotifyUserInfo)

"""Routing handler for /spotify"""
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from app.database.database import get_db_service
from app.database.service import DatabaseService
from app.settings import ENV_VARS
from app.spotify import models, schemas
from app.spotify.client import SpotifyAPIService
from tests.utils import generate_auth_state

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
    state = generate_auth_state()
    db_service.create(
        schemas.SpotifyAuthStateParam(id=state, user_id=user_id),
        models.SpotifyAuthStateParam,
    )
    auth_url = schemas.SpotifyAuthParams(state=state).format_as_url()

    return RedirectResponse(url=auth_url)


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
    auth_state_param = SpotifyAPIService.authorize_redirect_state(
        state=state, model_type=models.SpotifyAuthStateParam, db_service=db_service
    )

    token_response = SpotifyAPIService.exchange_code(code)
    user_response = SpotifyAPIService.get_user(token_response.access_token)

    spotify_user_info = schemas.SpotifyUserInfo(
        user_id=auth_state_param.user_id,
        **token_response.dict(),
        **user_response.dict(),
    )
    db_service.merge(input_schema=spotify_user_info, model_type=models.SpotifyUserInfo)

    return RedirectResponse(url=f"{ENV_VARS.FE_HOST}/spotify/{spotify_user_info.id}")

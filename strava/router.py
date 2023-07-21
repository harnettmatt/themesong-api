"""Routing handler for /strava"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

import settings
import utils
from database.database import get_db_service
from database.service import DatabaseService
from spotify.schemas import SpotifyTrack
from strava.client import StravaAPIService
from strava.handler import StravaWebhookHandler
from strava.models import StravaAuthStateParam
from strava.models import StravaUserInfo as StravaUserInfoModel
from strava.schemas import StravaAuthParams
from strava.schemas import StravaAuthStateParam as StravaAuthStateParamSchema
from strava.schemas import StravaUserInfo as StravaUserInfoSchema
from strava.schemas import StravaWebhookInput
from user.models import User
from user.schemas import UserCreate

ROUTER = APIRouter()


@ROUTER.get("/login")
def login(db_service: DatabaseService = Depends(get_db_service)):
    """
    Redirects to Strava login page
    """
    state = utils.generate_auth_state()
    db_service.create(
        StravaAuthStateParamSchema(id=state),
        StravaAuthStateParam,
    )
    auth_url = StravaAuthParams(state=state).format_as_url()

    return RedirectResponse(url=auth_url)


@ROUTER.get("/authorization")
def authorization(
    code: str, state: str, db_service: DatabaseService = Depends(get_db_service)
):
    """
    Redirect handler for when a Strava user grants access to the application
    Handler is responsible for:
        - swapping token for bearer and refresh
        - persisting relevant user information to the db

    Auth url:
    """
    StravaAPIService.authorize_redirect_state(
        state=state, model_type=StravaAuthStateParam, db_service=db_service
    )

    response = StravaAPIService.exchange_code(code)
    user = UserCreate(id=response.athlete.id)
    strava_user_info = StravaUserInfoSchema(
        id=user.id, user_id=user.id, **response.dict()
    )

    db_service.merge(input_schema=user, model_type=User)
    db_service.merge(input_schema=strava_user_info, model_type=StravaUserInfoModel)

    return RedirectResponse(url=f"http://localhost:5173/strava/{user.id}")


@ROUTER.get("/webhook", status_code=200)
def verify_webhook(request: Request):
    """
    Callback for event subscription for Strava
    """
    query_params = utils.get_query_params_as_dict(request)
    if (
        query_params.get("hub.mode") == "subscribe"
        and query_params.get("hub.verify_token")
        == settings.ENV_VARS.STRAVA_WEBHOOK_TOKEN
    ):
        return {"hub.challenge": query_params.get("hub.challenge")}

    raise HTTPException(403)


@ROUTER.post("/webhook", status_code=200, response_model=SpotifyTrack)
def receive_event(
    request_body: StravaWebhookInput,
    db_service: DatabaseService = Depends(get_db_service),
):
    """
    Recieves event from Strava for processing
    """
    # TODO: do i need to check that the request contains the verify_token? How do I know that the request is coming from Strava?
    return StravaWebhookHandler(request_body, db_service).handle()

"""Routing handler for /strava"""
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from app import settings, utils
from app.database.database import get_db_service
from app.database.service import DatabaseService
from app.spotify.schemas import SpotifyTrack
from app.strava.client import StravaAPIService
from app.strava.handler import StravaWebhookHandler
from app.strava.models import StravaAuthStateParam
from app.strava.models import StravaUserInfo as StravaUserInfoModel
from app.strava.schemas import StravaAuthParams
from app.strava.schemas import StravaAuthStateParam as StravaAuthStateParamSchema
from app.strava.schemas import StravaUserInfo as StravaUserInfoSchema
from app.strava.schemas import StravaWebhookInput
from app.user.models import User
from app.user.schemas import UserCreate

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

    return RedirectResponse(url=f"{settings.ENV_VARS.FE_HOST}/strava/{user.id}")


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
    print(f'webhook request: {json.dumps(request_body.json())}')
    # TODO: do i need to check that the request contains the verify_token? How do I know that the request is coming from Strava?
    return StravaWebhookHandler(request_body, db_service).handle()

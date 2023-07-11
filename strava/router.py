"""Routing handler for /strava"""
from fastapi import APIRouter, Depends, HTTPException, Request

import utils
from database.database import get_db_service
from database.service import DatabaseService
from settings import ENV_VARS
from strava.client import StravaAPIService
from strava.handler import StravaWebhookHandler
from strava.models import StravaUserInfo as StravaUserInfoModel
from strava.schemas import StravaUserInfo as StravaUserInfoSchema
from strava.schemas import StravaWebhookInput
from user.models import User
from user.schemas import UserCreate

ROUTER = APIRouter()


@ROUTER.get("/authorization", status_code=200)
def authorization(
    code: str, scope: str, db_service: DatabaseService = Depends(get_db_service)
):
    """
    Redirect handler for when a Strava user grants access to the application
    Handler is responsible for:
        - swapping token for bearer and refresh
        - persisting relevant user information to the db

    Auth url: http://www.strava.com/oauth/authorize?client_id=108820&response_type=code&redirect_uri=https://17dd-65-154-225-130.ngrok-free.app/strava/authorization&approval_prompt=force&scope=activity:read_all,activity:write
    """
    # TODO: check to make sure the correct permissions are granted, is there a specific error code that needs to be returned if this is unsuccessful
    response = StravaAPIService.exchange_code(code)

    user = UserCreate(id=response.athlete.id)
    # TODO: should we be generating our own user id?
    strava_user_info = StravaUserInfoSchema(
        id=user.id, user_id=user.id, **response.dict()
    )

    db_service.merge(input_schema=user, model_type=User)
    db_service.merge(input_schema=strava_user_info, model_type=StravaUserInfoModel)


@ROUTER.get("/webhook", status_code=200)
def verify_webhook(request: Request):
    """
    Callback for event subscription for Strava
    """
    query_params = utils.get_query_params_as_dict(request)
    if (
        query_params.get("hub.mode") == "subscribe"
        and query_params.get("hub.verify_token") == ENV_VARS.STRAVA_WEBHOOK_TOKEN
    ):
        return {"hub.challenge": query_params.get("hub.challenge")}

    raise HTTPException(403)


@ROUTER.post("/webhook", status_code=200)
def receive_event(
    request_body: StravaWebhookInput,
    db_service: DatabaseService = Depends(get_db_service),
):
    """
    Recieves event from Strava for processing
    """
    # TODO: do i need to check that the request contains the verify_token? How do I know that the request is coming from Strava?
    return StravaWebhookHandler(request_body, db_service).handle()

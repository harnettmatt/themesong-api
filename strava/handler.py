"""Routing handler for /strava"""
import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from requests import Response
from sqlalchemy.orm import Session

import utils
from database.database import get_session
from database.database_service import DatabaseService
from settings import ENV_VARS
from strava.schemas import (
    StravaOAauthTokenRequest,
    StravaOAuthTokenResponse,
    StravaUserInfo,
    StravaWebhookInput,
)
from strava.service import StravaUserInfoService
from user.schemas import UserCreate
from user.service import UserService

ROUTER = APIRouter()
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"


@ROUTER.get("/authorization", status_code=200)
def authorization(code: str, scope: str, session: Session = Depends(get_session)):
    """
    Redirect handler for when a Strava user grants access to the application
    Handler is responsible for:
        - swapping token for bearer and refresh
        - persisting relevant user information to the db

    Auth url: http://www.strava.com/oauth/authorize?client_id=108820&response_type=code&redirect_uri=https://17dd-65-154-225-130.ngrok-free.app/strava/authorization&approval_prompt=force&scope=activity:read_all,activity:write
    """
    # TODO: check to make sure the correct permissions are granted, is there a specific error code that needs to be returned if this is unsuccessful
    response: Response = requests.post(
        STRAVA_TOKEN_URL,
        params=StravaOAauthTokenRequest(code=code).dict(),
    )
    response_pydantic = StravaOAuthTokenResponse(**response.json())
    id = response_pydantic.athlete.id

    user = UserCreate(id=id)
    strava_user_info = StravaUserInfo(id=id, **response_pydantic.dict())

    db_service = DatabaseService(session)

    UserService(db_service=db_service).merge(user)
    StravaUserInfoService(db_service=db_service).merge(strava_user_info)


@ROUTER.post("/webhook", status_code=200)
async def receive_event(request_body: StravaWebhookInput):
    """
    Recieves event from Strava for processing
    """
    # TODO: do i need to check that the request contains the verify_token? How do I know that the request is coming from Strava?
    # TODO: look up token from db based on athlete id from strava
    # TODO: make call to strava to retrieve more information about activity
    # TODO: do i need to return something here. Check Strava docs if this doesn't work as is
    return


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
        print("WEBHOOK_VERIFIED")
        return {"hub.challenge": query_params.get("hub.challenge")}

    raise HTTPException(403)

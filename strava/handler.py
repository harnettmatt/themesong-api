"""Routing handler for /strava"""
from datetime import datetime, timedelta
from typing import Optional

import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from requests import Response
from sqlalchemy.orm import Session

import utils
from database.database import get_session
from database.database_service import DatabaseService
from settings import ENV_VARS
from strava.schemas import (
    StravaActivity,
    StravaAspectType,
    StravaOAauthTokenRequest,
    StravaOAuthTokenResponse,
    StravaObjectType,
    StravaUserInfo,
    StravaWebhookInput,
)
from strava.service import StravaUserInfoService
from user.schemas import UserCreate
from user.service import UserService

ROUTER = APIRouter()
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STAVA_API_PREFIX = "https://www.strava.com/api/v3"


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
    strava_user_info = StravaUserInfo(
        id=id, user_id=user.id, **response_pydantic.dict()
    )

    db_service = DatabaseService(session)

    UserService(db_service=db_service).merge(user)
    StravaUserInfoService(db_service=db_service).merge(strava_user_info)


# TODO: will we be able to process everything in 30 seconds? If not we can use a background task
@ROUTER.post("/webhook", status_code=200)
async def receive_event(
    request_body: StravaWebhookInput, session: Session = Depends(get_session)
):
    """
    Recieves event from Strava for processing
    """
    # TODO: do i need to check that the request contains the verify_token? How do I know that the request is coming from Strava?
    # TODO: move this all into a service
    if (
        request_body.aspect_type == StravaAspectType.UPDATE
        and request_body.object_type == StravaObjectType.ACTIVITY
    ):
        db_service = DatabaseService(session)
        user = UserService(db_service=db_service).get(request_body.owner_id)
        # TODO: create a strava service for this that handles token refreshing, headers, and prefixes better
        if user.strava_user_info.expires_at <= datetime.utcnow():  # type: ignore
            # TODO: refresh token
            pass

        # TODO: type the response
        response: Response = requests.get(
            f"{STAVA_API_PREFIX}/activities/{request_body.object_id}",
            headers={"Authorization": f"Bearer {user.strava_user_info.access_token}"},
        )
        activity = StravaActivity(
            **response.json()
        )  # TODO pydantic conversion for the response here
        response = requests.get(
            f"{STAVA_API_PREFIX}/activities/{activity.id}/streams?&keys=time,heartrate&key_by_type=true",
            headers={"Authorization": f"Bearer {user.strava_user_info.access_token}"},
        )
        body = response.json()
        max_hr_date_time = get_datetime_of_max_hr_for_activity_stream(
            activity_stream=body, activity_start_date=activity.start_date
        )
        print(max_hr_date_time)
        # TODO: get spotify history data for the time determined
        # TODO: update activity description with spotify song
        # TODO: update strava photos with a photo of the album art if user opts in
        # TODO: do i need to return something here. Check Strava docs if this doesn't work as is

    else:
        print("getting some different event")
    return


# TODO this can be a function on ActivityStream schema when that exists
def get_datetime_of_max_hr_for_activity_stream(
    activity_stream: dict, activity_start_date: datetime
) -> Optional[datetime]:
    hr_data = activity_stream["heartrate"]["data"]
    max_hr = max(hr_data)

    if max_hr > 0:
        seconds_elapsed = activity_stream["time"]["data"][hr_data.index(max_hr)]
        return activity_start_date + timedelta(seconds=seconds_elapsed)
    else:
        return None


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

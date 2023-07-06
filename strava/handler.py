"""Routing handler for /strava"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from requests import Response
from sqlalchemy.orm import Session

import utils
from database.database import get_session
from database.database_service import DatabaseService
from settings import ENV_VARS
from spotify.schemas import SpotifyTrack
from spotify.service import SpotifyAPIService
from strava.models import StravaUserInfo as StravaUserInfoModel
from strava.schemas import (
    StravaActivity,
    StravaAspectType,
    StravaOAauthTokenRequest,
    StravaOAuthTokenResponse,
    StravaObjectType,
)
from strava.schemas import StravaUserInfo as StravaUserInfoSchema
from strava.schemas import StravaWebhookInput
from user.models import User
from user.schemas import UserCreate

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
    strava_user_info = StravaUserInfoSchema(
        id=id, user_id=user.id, **response_pydantic.dict()
    )

    db_service = DatabaseService(session)

    db_service.merge(input_schema=user, model_type=User)
    db_service.merge(input_schema=strava_user_info, model_type=StravaUserInfoModel)


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
        or request_body.aspect_type == StravaAspectType.CREATE
    ) and request_body.object_type == StravaObjectType.ACTIVITY:
        db_service = DatabaseService(session)
        user = db_service.get(id=request_body.owner_id, model_type=User)
        # TODO: create a strava service for this that handles token refreshing, headers, and prefixes better
        # TODO: we might want to just disable mypy entirely because of this interaction with sqlalchemy.
        #       mypy treats all non-id fields as optional which causes issues with statements like these
        if user.strava_user_info.expires_at <= datetime.utcnow():  # type: ignore
            # TODO: refresh token
            pass

        # TODO: use Strava sdk
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
        if max_hr_date_time is not None:
            track = get_spotify_track_for_datetime(
                user=user, max_hr_date_time=max_hr_date_time
            )
            if track is not None:
                response = requests.put(
                    f"{STAVA_API_PREFIX}/activities/{activity.id}",
                    headers={
                        "Authorization": f"Bearer {user.strava_user_info.access_token}"
                    },
                    data={
                        "description": f"{activity.description} \nTheme Song: {track.name} - {track.href}"
                    },
                )
            else:
                # TODO: try and atempt with the next highest heart rate
                print("could not find track")
        # TODO: do i need to return something here. Check Strava docs if this doesn't work as is

    else:
        print("getting some different event")
    return


# TODO: move this into a service
class SearchDirection(Enum):
    EARLIER = "earlier"
    LATER = "later"


# TODO: move this into a service
def get_spotify_track_for_datetime(
    user: User, max_hr_date_time: datetime
) -> Optional[SpotifyTrack]:
    user_history_response = SpotifyAPIService().get_user_history(
        access_token=user.spotify_user_info.access_token, after=max_hr_date_time - timedelta(minutes=30)  # type: ignore
    )
    user_history_response.items.reverse()
    for play_history_item in user_history_response.items:
        end_time = play_history_item.played_at
        start_time = end_time - timedelta(
            milliseconds=play_history_item.track.duration_ms
        )
        # max_hr_date_time falls within track time
        if start_time <= max_hr_date_time and max_hr_date_time <= end_time:
            return play_history_item.track
        # max_hr_date_time is later than the track
        elif start_time < max_hr_date_time and end_time < max_hr_date_time:
            continue
        # max_hr_date_time is earlier than the track
        else:
            raise Exception("Didn't search for tracks far enough back in time")

    return None


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

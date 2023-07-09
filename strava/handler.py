"""Routing handler for /strava"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request

import utils
from database.database import get_db_service
from database.database_service import DatabaseService
from settings import ENV_VARS
from spotify.schemas import SpotifyTrack
from spotify.service import SpotifyAPIService
from strava.models import StravaUserInfo as StravaUserInfoModel
from strava.schemas import StravaAspectType, StravaObjectType
from strava.schemas import StravaUserInfo as StravaUserInfoSchema
from strava.schemas import StravaWebhookInput
from strava.service import StravaAPIService, StreamKeys
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


@ROUTER.post("/webhook", status_code=200)
async def receive_event(
    request_body: StravaWebhookInput,
    db_service: DatabaseService = Depends(get_db_service),
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
        user = db_service.get(id=request_body.owner_id, model_type=User)

        strava_api_service = StravaAPIService(
            StravaUserInfoSchema.from_orm(user.strava_info), db_service=db_service
        )
        activity = strava_api_service.get_activity(request_body.object_id)
        activity_stream = strava_api_service.get_stream_for_activity(
            id=activity.id, stream_keys=[StreamKeys.TIME, StreamKeys.HEARTRATE]
        )
        max_hr_time_mark = activity_stream.get_max_heartrate_time_mark()
        if max_hr_time_mark is None:
            print("could not find track")
            return

        max_hr_date_time = activity.start_date + max_hr_time_mark
        track = get_spotify_track_for_datetime(
            user=user, max_hr_date_time=max_hr_date_time
        )
        if track is None:
            # TODO: try and atempt with the next highest heart rate
            print("could not find track")
            return
        strava_api_service.update_activity(
            id=activity.id,
            data={
                "description": f"{activity.description} \nTheme Song: {track.name} - {track.href}"
            },
        )
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
    user_history_response = SpotifyAPIService(
        token=user.spotify_user_info.access_token
    ).get_user_history(
        after=max_hr_date_time - timedelta(minutes=30)  # type: ignore
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

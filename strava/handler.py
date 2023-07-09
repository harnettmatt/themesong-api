"""Routing handler for /strava"""
from fastapi import APIRouter, Depends, HTTPException, Request

import utils
from database.database import get_db_service
from database.database_service import DatabaseService
from settings import ENV_VARS
from spotify.schemas import SpotifyUserInfo
from spotify.service import SpotifyAPIService, SpotifyService
from strava.models import StravaUserInfo as StravaUserInfoModel
from strava.schemas import StravaAspectType, StravaObjectType
from strava.schemas import StravaUserInfo as StravaUserInfoSchema
from strava.schemas import StravaWebhookInput
from strava.service import StravaAPIService, StravaService
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
        # get user
        user = db_service.get(id=request_body.owner_id, model_type=User)

        # setup services
        strava_api_service = StravaAPIService(
            StravaUserInfoSchema.from_orm(user.strava_info), db_service=db_service
        )
        strava_service = StravaService(api=strava_api_service)
        spotify_api_service = SpotifyAPIService(
            user_info=SpotifyUserInfo.from_orm(user.spotify_user_info),
            db_service=db_service,
        )
        spotify_service = SpotifyService(api=spotify_api_service)

        # get activity and max hr
        activity = strava_service.api.get_activity(request_body.object_id)
        max_hr_date_time = strava_service.get_max_hr_date_time_for_activity(activity)
        if max_hr_date_time is None:
            print("could not find max hr")
            return

        # get track
        track = spotify_service.get_track_for_datetime(max_hr_date_time)
        if track is None:
            print("could not find track")
            return

        # update activity
        strava_service.update_activity_with_track(activity, track)
        # TODO: do i need to return something here. Check Strava docs if this doesn't work as is
    else:
        print("getting some different event")
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

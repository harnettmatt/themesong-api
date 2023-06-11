"""Routing handler for /strava"""
from fastapi import APIRouter, HTTPException, Request

import utils
from strava.schemas import StravaWebhookInput

ROUTER = APIRouter()

# TODO: create callback for strava authorization. This endpoint should persist the athlete id and token


@ROUTER.post("/webhook", status_code=200)
async def receive_event(request_body: StravaWebhookInput):
    """
    Recieves event from Strava for processing
    """
    # TODO: look up token from db based on athlete id from strava
    # TODO: make call to strava to retrieve more information about activity
    # TODO: do i need to return something here. Check Strava docs if this doesn't work as is
    return


@ROUTER.get("/webhook", status_code=200)
def verify_webhook(request: Request):
    """
    Callback for event subscription for Strava
    """
    # TODO: store token somewhere
    verify_token = "71998eb6-d783-4dc6-b287-fc74c23d4c42"

    query_params = utils.get_query_params_as_dict(request)
    if (
        query_params.get("hub.mode") == "subscribe"
        and query_params.get("hub.verify_token") == verify_token
    ):
        print("WEBHOOK_VERIFIED")
        return {"hub.challenge": query_params.get("hub.challenge")}

    raise HTTPException(403)

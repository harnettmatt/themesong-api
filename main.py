"""Routing handler for /"""
from fastapi import FastAPI

from strava.handler import ROUTER as STRAVA_HANDLER
from user.handler import ROUTER as USERS_ROUTER

app = FastAPI()

app.include_router(STRAVA_HANDLER, prefix="/strava", tags=["strava"])
app.include_router(USERS_ROUTER, prefix="/users", tags=["users"])

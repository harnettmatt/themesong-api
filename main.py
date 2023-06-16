"""Routing handler for /"""
from fastapi import FastAPI

from spotify.handler import ROUTER as SPOTIFY_ROUTER
from strava.handler import ROUTER as STRAVA_ROUTER
from user.handler import ROUTER as USERS_ROUTER

app = FastAPI()

app.include_router(SPOTIFY_ROUTER, prefix="/spotify", tags=["spotify"])
app.include_router(STRAVA_ROUTER, prefix="/strava", tags=["strava"])
app.include_router(USERS_ROUTER, prefix="/users", tags=["users"])

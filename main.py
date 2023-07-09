"""Routing for /"""
from fastapi import FastAPI

from spotify.router import ROUTER as SPOTIFY_ROUTER
from strava.router import ROUTER as STRAVA_ROUTER
from user.router import ROUTER as USERS_ROUTER

app = FastAPI()

app.include_router(SPOTIFY_ROUTER, prefix="/spotify", tags=["spotify"])
app.include_router(STRAVA_ROUTER, prefix="/strava", tags=["strava"])
app.include_router(USERS_ROUTER, prefix="/users", tags=["users"])

"""Routing for /"""
import logging

from fastapi import FastAPI

from app.health import ROUTER as HEALTH_ROUTER
from app.settings import ENV_VARS
from app.spotify.router import ROUTER as SPOTIFY_ROUTER
from app.strava.router import ROUTER as STRAVA_ROUTER
from app.user.router import ROUTER as USERS_ROUTER

logging.basicConfig(level=ENV_VARS.LOG_LEVEL)

app = FastAPI()

app.include_router(SPOTIFY_ROUTER, prefix="/spotify", tags=["spotify"])
app.include_router(STRAVA_ROUTER, prefix="/strava", tags=["strava"])
app.include_router(USERS_ROUTER, prefix="/users", tags=["users"])
app.include_router(HEALTH_ROUTER, prefix="/health", tags=["health"])

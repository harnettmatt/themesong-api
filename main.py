"""Routing handler for /"""
from fastapi import FastAPI

from webhook.handler import ROUTER as WEBHOOK_ROUTER
from user.handler import ROUTER as USERS_ROUTER

app = FastAPI()

app.include_router(WEBHOOK_ROUTER, prefix="/webhook", tags=["webhook"])
app.include_router(USERS_ROUTER, prefix="/users", tags=["users"])

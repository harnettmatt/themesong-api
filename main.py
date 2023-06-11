"""Routing handler for /"""
from fastapi import FastAPI

from group.handler import ROUTER as GROUPS_ROUTER
from item.handler import ROUTER as ITEMS_ROUTER
from membership.handler import ROUTER as MEMBERSHIPS_ROUTER
from user.handler import ROUTER as USERS_ROUTER

APP = FastAPI()

APP.include_router(GROUPS_ROUTER, prefix="/groups")
APP.include_router(ITEMS_ROUTER, prefix="/items")
APP.include_router(USERS_ROUTER, prefix="/users")
APP.include_router(MEMBERSHIPS_ROUTER, prefix="/memberships")

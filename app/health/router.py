"""Routing handler for /health"""
from fastapi import APIRouter, Depends
from urllib3 import HTTPResponse

from app.database.database import get_db_service
from app.database.service import DatabaseService

ROUTER = APIRouter()


@ROUTER.get("/")
def login(db_service: DatabaseService = Depends(get_db_service)):
    """
    Redirects to Strava login page
    """
    return HTTPResponse(status=200)

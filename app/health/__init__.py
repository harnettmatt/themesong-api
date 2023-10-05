"""Routing handler for /health"""
from fastapi import APIRouter, Depends

from app.database.database import get_db_service
from app.database.service import DatabaseService

ROUTER = APIRouter()


@ROUTER.get("/", status_code=200)
def health(db_service: DatabaseService = Depends(get_db_service)):
    """
    Endpoint for checking health of the application
    """
    return {"status": "healthy"}

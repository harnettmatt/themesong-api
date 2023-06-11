"""Routing handler for /memberships"""
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.utils import get_current_user_id
from database.database import get_session
from database.database_service import DatabaseService
from membership import models, schemas

ROUTER = APIRouter()


@ROUTER.get("/", response_model=list[schemas.Membership])
def get_all(
    session: Session = Depends(get_session), user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Gets all memberships
    """
    return DatabaseService(session).all(model_type=models.Membership)


@ROUTER.get("/{id}", response_model=schemas.Membership)
def get(
    id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> Any:
    """
    Gets a membership by id
    """
    return DatabaseService(session).get(id=id, model_type=models.Membership)


@ROUTER.post("/", response_model=schemas.Membership)
def create(
    input: schemas.MembershipCreate,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> Any:
    """
    Creates a membership
    """
    return DatabaseService(session).create(
        input_schema=input, model_type=models.Membership
    )


@ROUTER.delete("/{id}", response_model=schemas.Membership)
def delete(
    id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> Any:
    """
    Deletes a membership by id
    """
    return DatabaseService(session).delete(id=id, model_type=models.Membership)

"""Routing handler for /groups"""
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.utils import get_current_user_id
from database.database import get_session
from database.database_service import DatabaseService
from group import models, schemas

ROUTER = APIRouter()


@ROUTER.get("/", response_model=list[schemas.Group])
def get_all(
    session: Session = Depends(get_session), user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Gets all groups
    """
    return DatabaseService(session).all(model_type=models.Group)


@ROUTER.get("/{id}", response_model=schemas.Group)
def get(
    id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> Any:
    """
    Gets a group by id
    """
    return DatabaseService(session).get(id=id, model_type=models.Group)


@ROUTER.post("/", response_model=schemas.Group)
def create(
    input: schemas.GroupCreate,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> Any:
    """
    Creates a group
    """
    return DatabaseService(session).create(input_schema=input, model_type=models.Group)


@ROUTER.patch("/{id}", response_model=schemas.Group)
def update(
    id: int,
    input: schemas.GroupUpdate,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> Any:
    """
    Patch a group by id
    """
    return DatabaseService(session).update(
        id=id, input_schema=input, model_type=models.Group
    )


@ROUTER.delete("/{id}", response_model=schemas.Group)
def delete(
    id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> Any:
    """
    Deletes a group by id
    """
    return DatabaseService(session).delete(id=id, model_type=models.Group)

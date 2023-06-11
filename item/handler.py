"""Routing handler for /items"""
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.utils import get_current_user_id
from database.database import get_session
from database.database_service import DatabaseService
from item import models, schemas

ROUTER = APIRouter()


@ROUTER.get("/", response_model=list[schemas.Item])
def get_all(
    session: Session = Depends(get_session), user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Gets all items
    """
    return DatabaseService(session).all(model_type=models.Item)


@ROUTER.get("/{id}", response_model=schemas.Item)
def get(
    id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> Any:
    """
    Gets a item by id
    """
    return DatabaseService(session).get(id=id, model_type=models.Item)


@ROUTER.post("/", response_model=schemas.Item)
def create(
    input: schemas.ItemCreate,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> Any:
    """
    Creates a item
    """
    return DatabaseService(session).create(input_schema=input, model_type=models.Item)


@ROUTER.patch("/{id}", response_model=schemas.Item)
def update(
    id: int,
    input: schemas.ItemUpdate,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> Any:
    """
    Patch a item by id
    """
    return DatabaseService(session).update(
        id=id, input_schema=input, model_type=models.Item
    )


@ROUTER.delete("/{id}", response_model=schemas.Item)
def delete(
    id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> Any:
    """
    Deletes a item by id
    """
    return DatabaseService(session).delete(id=id, model_type=models.Item)

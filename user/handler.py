"""Routing handler for /users"""
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.utils import get_current_user_id
from database.database import get_session
from database.database_service import DatabaseService
from user import models, schemas

ROUTER = APIRouter()


@ROUTER.get("/", response_model=list[schemas.User])
def get_all(
    session: Session = Depends(get_session), user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Gets all users
    """
    return DatabaseService(session).all(model_type=models.User)


@ROUTER.get("/{id}", response_model=schemas.User)
def get(
    id: str,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> Any:
    """
    Gets a user by id
    """
    return DatabaseService(session).get(id=id, model_type=models.User)


@ROUTER.post("/", response_model=schemas.User)
def create(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> Any:
    """
    Creates a user
    """
    input = schemas.UserCreate(id=user_id)
    return DatabaseService(session).create(input_schema=input, model_type=models.User)


# uncommment when patching is supported
# @ROUTER.patch("/{id}", response_model=schemas.User)
# def update(
#     id: int,
#     input: schemas.UserUpdate,
#     session: Session = Depends(get_session),
#     user_id: str = Depends(get_current_user_id),
# ) -> Any:
#     """
#     Patch a user by id
#     """
#     return DatabaseService(session).update(
#         id=id, input_schema=input, model_type=models.User
#     )


@ROUTER.delete("/{id}", response_model=schemas.User)
def delete(
    id: str,
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> Any:
    """
    Deletes a user by id
    """
    return DatabaseService(session).delete(id=id, model_type=models.User)

"""Module containing sqlalchemy models"""
from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from persistable.models import Persistable


class User(Persistable):
    """
    SqlAlchemy model
    """

    __tablename__ = "users"

    # attributes
    id = Column(Integer, primary_key=True, index=True)

    # relationships
    # TODO: figure out why mypy doesn't like this
    strava_user_info = relationship("StravaUserInfo", back_populates="user")  # type: ignore

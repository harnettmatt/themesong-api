"""Module containing sqlalchemy models"""
from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from persistable.models import Persistable
from spotify.models import SpotifyUserInfo
from strava.models import StravaUserInfo


class User(Persistable):
    """
    SqlAlchemy model
    """

    __tablename__ = "users"

    # attributes
    id = Column(Integer, primary_key=True, index=True)

    # relationships
    # FIXME: fix 1:1 relationship
    strava_user_info = relationship(StravaUserInfo, back_populates="user", uselist=False)  # type: ignore
    spotify_user_info = relationship(
        SpotifyUserInfo, back_populates="user", uselist=False
    )  # type: ignore

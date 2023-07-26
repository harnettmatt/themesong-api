"""Module containing sqlalchemy models"""
from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from app.persistable.models import Persistable
from app.spotify.models import SpotifyUserInfo
from app.strava.models import StravaUserInfo


class User(Persistable):
    """
    SqlAlchemy model
    """

    __tablename__ = "users"

    # attributes
    id = Column(Integer, primary_key=True, index=True)

    # relationships
    strava_user_info = relationship(StravaUserInfo, uselist=False)
    spotify_user_info = relationship(SpotifyUserInfo, uselist=False)

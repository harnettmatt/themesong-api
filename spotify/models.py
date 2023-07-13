from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from persistable.models import Persistable


class SpotifyUserInfo(Persistable):
    """
    SqlAlchemy model
    """

    __tablename__ = "spotify_user_info"

    # attributes
    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    access_token = Column(String)
    refresh_token = Column(String)
    expires_in = Column(Integer)

    # relationships
    # FIXME: figure out why mypy doesn't like this
    user = relationship("User", back_populates="spotify_user_info")  # type: ignore


class SpotifyAuthStateParam(Persistable):
    """
    SqlAlchemy model
    """

    __tablename__ = "spotify_auth_state_param"

    # attributes
    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

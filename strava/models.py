from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from persistable.models import Persistable


class StravaUserInfo(Persistable):
    """
    SqlAlchemy model
    """

    __tablename__ = "strava_user_info"

    # attributes
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    access_token = Column(String)
    refresh_token = Column(String)
    expires_at = Column(String)

    # relationships
    # FIXME: fix 1:1 relationship
    user = relationship("User", back_populates="strava_user_info")  # type: ignore


class StravaAuthStateParam(Persistable):
    """
    SqlAlchemy model
    """

    __tablename__ = "strava_auth_state_param"

    # attributes
    id = Column(String, primary_key=True, index=True)

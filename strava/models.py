from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
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
    expires_at = Column(DateTime)

    # relationships
    # TODO: figure out why mypy doesn't like this
    user = relationship("User", back_populates="strava_user_info")  # type: ignore

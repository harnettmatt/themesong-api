from sqlalchemy import Column, ForeignKey, Integer, String

from app.persistable.models import Persistable


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


class StravaAuthStateParam(Persistable):
    """
    SqlAlchemy model
    """

    __tablename__ = "strava_auth_state_param"

    # attributes
    id = Column(String, primary_key=True, index=True)

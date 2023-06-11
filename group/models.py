"""Module containing sqlalchemy models"""
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from item.models import Item  # noqa
from persistable.models import Persistable
from user.models import User  # noqa


class Group(Persistable):
    """
    SqlAlchemy model
    """

    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    user_id = Column(String, ForeignKey("users.id"))

    items = relationship("Item", secondary="memberships")
    user = relationship("User")

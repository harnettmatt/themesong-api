"""Module containing sqlalchemy models"""
from sqlalchemy import Column, String

from persistable.models import Persistable


class User(Persistable):
    """
    SqlAlchemy model
    """

    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)

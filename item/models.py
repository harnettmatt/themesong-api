"""Module containing sqlalchemy models"""
from sqlalchemy import Column, Integer, String

from persistable.models import Persistable


class Item(Persistable):
    """
    SqlAlchemy model
    """

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

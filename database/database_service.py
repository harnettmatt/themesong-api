"""Module responsible for interacting with db via sqlalchemy"""
from typing import Type, Union

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from persistable.models import Persistable

# User id is defined as a string and all other ids are autoincrementing
ID = Union[str, int]


class DatabaseService:
    """
    Service that interacts with the db
    """

    session: Session

    def __init__(self, session: Session):
        self.session = session

    def get(self, id: ID, model_type: Type[Persistable]):
        """
        Gets object from db for a given model and id
        """
        user = self.session.query(model_type).get(id)
        if user is None:
            raise HTTPException(404, "Not Found")

        return user

    def all(self, model_type: Type[Persistable], skip: int = 0, limit: int = 100):
        """
        Gets all objects from db for a given model and optional limiting
        """
        return self.session.query(model_type).offset(skip).limit(limit).all()

    def create(self, input_schema: BaseModel, model_type: Type[Persistable]):
        """
        Creates object in db for a given pydantic input schema and model
        """
        model_object = model_type(**jsonable_encoder(input_schema))

        self.session.add(model_object)
        self.session.commit()

        return model_object

    def delete(self, id: ID, model_type: Type[Persistable]):
        """
        Deletes object from db for a given model and id
        """
        model_object = self.get(id=id, model_type=model_type)
        self.session.delete(model_object)
        self.session.commit()

        return model_object

    def update(self, id: ID, input_schema: BaseModel, model_type: Type[Persistable]):
        """
        Gets object from db, merges input_schema with db object, update db object
        """
        model_object = self.get(id=id, model_type=model_type)
        updated_model_object = self._update_model_object_from_input(
            input=input_schema, model_object=model_object
        )

        self.session.add(updated_model_object)
        self.session.commit()

        return updated_model_object

    def merge(self, input_schema: BaseModel, model_type: Type[Persistable]):
        """
        Updates object if exists in db, otherwise creates db object
        """
        model_object = model_type(**jsonable_encoder(input_schema))

        self.session.merge(model_object)
        self.session.commit()

        return model_object

    @classmethod
    def _update_model_object_from_input(
        cls, input: BaseModel, model_object: Persistable
    ) -> Persistable:
        """
        Converts input and model_object to dicts and updates model_object
        """
        update_dict = input.dict(exclude_none=True)
        model_object_dict = jsonable_encoder(model_object)

        for key, val in update_dict.items():
            if key in model_object_dict:
                setattr(model_object, key, val)

        return model_object

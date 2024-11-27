"""Module responsible for interacting with db via sqlalchemy"""
import logging
from typing import Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.persistable.models import Persistable

# User id is defined as a string and all other ids are autoincrementing
ID = Union[str, int]
P = TypeVar("P", bound=Persistable)


class DatabaseService:
    """
    Service that interacts with the db
    """

    session: Session

    def __init__(self, session: Session):
        self.session = session

    def get(self, id: ID, model_type: Type[P]) -> Optional[P]:
        """
        Gets object from db for a given model and id
        """
        logging.debug(f'DB Service getting type: {model_type} for id: {id}')
        return self.session.query(model_type).get(id)

    def all(self, model_type: Type[P], skip: int = 0, limit: int = 100) -> list[P]:
        """
        Gets all objects from db for a given model and optional limiting
        """
        logging.debug(f'DB Service getting all: {model_type}')
        return self.session.query(model_type).offset(skip).limit(limit).all()

    def create(self, input_schema: BaseModel, model_type: Type[P]):
        """
        Creates object in db for a given pydantic input schema and model
        """
        model_object = model_type(**jsonable_encoder(input_schema))

        logging.debug(f'DB Service creating: {model_object}')
        self.session.add(model_object)
        self.session.commit()

        return model_object

    def delete(self, id: ID, model_type: Type[P]) -> Optional[P]:
        """
        Deletes object from db for a given model and id
        """
        model_object = self.get(id=id, model_type=model_type)
        if model_object is None:
            return None

        logging.debug(f'DB Service deleting: {model_object}')
        return self.delete_instance(model=model_object)

    def delete_instance(self, model: P) -> P:
        """
        Deletes object from db
        """
        logging.debug(f'DB Service deleting instance: {model}')
        self.session.delete(model)
        self.session.commit()

        return model

    def update(
        self, id: ID, input_schema: BaseModel, model_type: Type[P]
    ) -> Optional[P]:
        """
        Gets object from db, merges input_schema with db object, update db object
        """
        model_object = self.get(id=id, model_type=model_type)
        if model_object is None:
            return None

        updated_model_object = self._update_model_object_from_input(
            input=input_schema, model_object=model_object
        )

        logging.debug(f'DB Service updating: {model_object}')
        self.session.add(updated_model_object)
        self.session.commit()

        return updated_model_object

    def merge(self, input_schema: BaseModel, model_type: Type[P]) -> P:
        """
        Updates object if exists in db, otherwise creates db object
        """
        model_object = model_type(**jsonable_encoder(input_schema))

        logging.debug(f'DB Service merging: {model_object}')
        self.session.merge(model_object)
        self.session.commit()

        return model_object

    @classmethod
    def _update_model_object_from_input(cls, input: BaseModel, model_object: P) -> P:
        """
        Converts input and model_object to dicts and updates model_object
        """
        update_dict = input.dict(exclude_none=True)
        model_object_dict = jsonable_encoder(model_object)

        for key, val in update_dict.items():
            if key in model_object_dict:
                setattr(model_object, key, val)

        return model_object

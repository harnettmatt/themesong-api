from typing import Optional

from sqlalchemy import Column, Integer, String

from app.database.service import DatabaseService
from app.persistable.models import Persistable


class MockSchemaCreate:
    """
    Test schema create
    """

    name: str
    other: Optional[str] = None


class MockModel(Persistable):
    """
    Test model
    """

    __tablename__ = "mock"

    # attributes
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    other = Column(String, nullable=True)


def test_get(local_session):
    """
    Tests get method
    """
    # Arrange
    service = DatabaseService(session=local_session)
    model_object = service.create(
        input_schema=MockSchemaCreate(name="test"), model_type=MockModel
    )
    # Act
    result = service.get(id=model_object.id, model_type=MockModel)
    # Assert
    assert result is not None
    assert result.id == model_object.id
    assert result.name == model_object.name
    assert result.other == model_object.other


def test_get_none(local_session):
    """
    Tests get method
    """
    # Arrange
    service = DatabaseService(session=local_session)
    # Act
    result = service.get(id=1, model_type=MockModel)
    # Assert
    assert result is None


def test_all(local_session):
    """
    Tests all method
    """
    # Arrange
    service = DatabaseService(session=local_session)
    model_object = service.create(
        input_schema=MockSchemaCreate(name="test"), model_type=MockModel
    )
    # Act
    result = service.all(model_type=MockModel)
    # Assert
    assert result is not None
    assert len(result) == 1
    assert result[0].id == model_object.id
    assert result[0].name == model_object.name
    assert result[0].other == model_object.other


def test_all_empty(local_session):
    """
    Tests all method
    """
    # Arrange
    service = DatabaseService(session=local_session)
    # Act
    result = service.all(model_type=MockModel)
    # Assert
    assert result is not None
    assert len(result) == 0


def test_create(local_session):
    """
    Tests create method
    """
    # Arrange
    service = DatabaseService(session=local_session)
    # Act
    result = service.create(
        input_schema=MockSchemaCreate(name="test"), model_type=MockModel
    )
    # Assert
    assert result is not None
    assert result.id is not None
    assert result.name == "test"
    assert result.other is None
    assert local_session.query(MockModel).get(result.id) == result


def test_delete(local_session):
    """
    Tests delete method
    """
    # Arrange
    service = DatabaseService(session=local_session)
    model_object = service.create(
        input_schema=MockSchemaCreate(name="test"), model_type=MockModel
    )
    # Act
    result = service.delete(id=model_object.id, model_type=MockModel)
    # Assert
    assert result is not None
    assert result.id == model_object.id
    assert result.name == model_object.name
    assert result.other == model_object.other
    assert local_session.query(MockModel).get(result.id) is None


def test_delete_none(local_session):
    """
    Tests delete method
    """
    # Arrange
    service = DatabaseService(session=local_session)
    # Act
    result = service.delete(id=1, model_type=MockModel)
    # Assert
    assert result is None


def test_update(local_session):
    """
    Tests update method
    """
    # Arrange
    service = DatabaseService(session=local_session)
    model_object = service.create(
        input_schema=MockSchemaCreate(name="test"), model_type=MockModel
    )
    # Act
    result = service.update(
        id=model_object.id,
        input_schema=MockSchemaCreate(name="test2"),
        model_type=MockModel,
    )
    # Assert
    assert result is not None
    assert result.id == model_object.id
    assert result.name == "test2"
    assert result.other == model_object.other
    assert local_session.query(MockModel).get(result.id) == result


def test_update_none(local_session):
    """
    Tests update method
    """
    # Arrange
    service = DatabaseService(session=local_session)
    # Act
    result = service.update(
        id=1,
        input_schema=MockSchemaCreate(name="test2"),
        model_type=MockModel,
    )
    # Assert
    assert result is None


def test_update_model_object_from_input(local_session):
    """
    Tests update method
    """
    # Arrange
    model_object = MockModel(name="test", other="other")
    # Act
    result = DatabaseService._update_model_object_from_input(
        input=MockSchemaCreate(name="test2"), model_object=model_object
    )
    # Assert
    assert result is not None
    assert result.id == model_object.id
    assert result.name == "test2"
    assert result.other == "other"

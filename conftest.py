# import random
# import string

# import pytest
# from fastapi import HTTPException
# from fastapi.testclient import TestClient
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# from auth.utils import get_current_user_id
# from database.database import get_session
# from database.database_service import DatabaseService
# from main import app
# from persistable.models import Base
# from user import models as user_models
# from user import schemas as user_schemas

# # CONSTANTS
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# MOCK_USER_ID = "auth0|1234567890abcdefghijklmn"

# # TEST DB SETUP
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base.metadata.create_all(bind=engine)


# # app OVERRIDES
# def override_get_session():
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# def override_get_token():
#     return True


# def override_get_current_user_id():
#     return MOCK_USER_ID


# app.dependency_overrides[get_session] = override_get_session
# app.dependency_overrides[get_current_user_id] = override_get_current_user_id


# # TEST CLIENT WITH OVERRIDES
# @pytest.fixture(name="test_client")
# def fixture_test_client():
#     return TestClient(app)


# # FIXTURES
# @pytest.fixture(name="mock_random_user_id")
# def mock_random_user_id() -> str:
#     return (
#         f'auth0|{"".join(random.choices(string.ascii_letters + string.digits, k=24))}'
#     )


# @pytest.fixture(autouse=True)
# def seed_constant_mock_user():
#     db_service = DatabaseService(next(override_get_session()))
#     try:
#         db_service.get(id=MOCK_USER_ID, model_type=user_models.User)
#     except HTTPException as error:
#         if error.status_code == 404:
#             user_input = user_schemas.UserCreate(id=MOCK_USER_ID)
#             db_service.create(input_schema=user_input, model_type=user_models.User)
#         else:
#             raise error


# @pytest.fixture(name="mock_random_user")
# def mock_user(mock_random_user_id) -> user_models.User:
#     user_input = user_schemas.UserCreate(id=mock_random_user_id)
#     return DatabaseService(next(override_get_session())).create(
#         input_schema=user_input, model_type=user_models.User
#     )

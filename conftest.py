import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import settings
from database.database import get_session
from persistable.models import Base

settings.ENV_VARS = settings.EnvironmentVariables(
    HOST="https://123abctest.com",
    STRAVA_CLIENT_ID=1234567890,
    STRAVA_CLIENT_SECRET="abcdefghijk",
    STRAVA_WEBHOOK_TOKEN="abc123",
    SPOTIFY_CLIENT_ID="0987654321",
    SPOTIFY_CLIENT_SECRET="lmnopqrstuv",
)

from main import app  # noqa: E402

# CONSTANTS
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# TEST DB SETUP
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    """Fixture to execute before and after a test is run"""
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


def get_local_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def local_session():
    return next(get_local_db())


app.dependency_overrides[get_session] = get_local_db


@pytest.fixture(name="test_client")
def fixture_test_client():
    return TestClient(app)

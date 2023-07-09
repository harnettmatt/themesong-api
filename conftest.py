import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from persistable.models import Base

# CONSTANTS
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
MOCK_USER_ID = "auth0|1234567890abcdefghijklmn"

# TEST DB SETUP
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def local_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

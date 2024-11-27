"""Module containing all database setup"""
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import base  # noqa
from app.database.service import DatabaseService
from app.persistable.models import Base
from app.settings import ENV_VARS

SQLALCHEMY_DATABASE_URL = f"postgresql://{ENV_VARS.DB_USER}:{ENV_VARS.DB_PASSWORD}@{ENV_VARS.DB_HOST}:{ENV_VARS.DB_PORT}/{ENV_VARS.DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(engine)


def get_session():
    """
    Helper function responsible for creating a db session
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_db_service(session: Session = Depends(get_session)):
    return DatabaseService(session)

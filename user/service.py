from database.database_service import DatabaseService
from user import models, schemas


class UserService:
    db_service: DatabaseService

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def merge(self, user: schemas.UserCreate):
        self.db_service.merge(input_schema=user, model_type=models.User)

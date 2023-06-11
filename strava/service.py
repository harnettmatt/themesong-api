from database.database_service import DatabaseService
from strava import models, schemas


class StravaUserInfoService:
    db_service: DatabaseService

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def merge(self, strava_user_info: schemas.StravaUserInfo):
        self.db_service.merge(
            input_schema=strava_user_info, model_type=models.StravaUserInfo
        )

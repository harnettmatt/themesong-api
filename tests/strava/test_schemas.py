from app.strava.schemas import StravaActivity


def test_datetime_format():
    body = {"id": 1, "start_date": "2023-10-08T08:39:56+00:00"}
    strava_activity = StravaActivity(**body)
    assert strava_activity.start_date.tzname() == "UTC"

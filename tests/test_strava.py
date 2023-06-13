import json
from datetime import datetime

from strava.handler import get_datetime_of_max_hr_for_activity_stream


def test_get_datetime_of_max_har_for_activity_stream():
    f = open("./tests/test_data/stream.json")
    stream_data = json.load(f)

    max_hr_datetime = get_datetime_of_max_hr_for_activity_stream(
        activity_stream=stream_data,
        activity_start_date=datetime(2023, 1, 1, 0, 0, 0, 0),
    )
    assert max_hr_datetime == datetime(2023, 1, 1, 0, 0, 29)

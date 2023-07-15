from datetime import datetime

import pytest

from spotify.schemas import SpotifyTrack
from strava.schemas import StravaActivity
from strava.service import StravaService


@pytest.mark.parametrize(
    "description", [None, "", "Test Description", "Theme Song: Existing Track"]
)
def test_update_activity_with_track(description, mocker):
    # Arrange
    api = mocker.MagicMock()
    service = StravaService(api=api)
    activity = StravaActivity(
        id=1,
        description=description,
        start_date=datetime(2021, 1, 1),
    )
    track = SpotifyTrack(
        id="123",
        duration_ms=123,
        name="Test Track",
        href="https://open.spotify.com/track/123",
    )
    # Act
    service.update_activity_with_track(activity=activity, track=track)
    # Assert
    if description is None or description == "":
        api.update_activity.assert_called_once_with(
            id=1,
            data={
                "description": "Theme Song: Test Track - https://open.spotify.com/track/123"
            },
        )
    elif "Theme Song:" in description:
        api.update_activity.assert_not_called()
    else:
        api.update_activity.assert_called_once_with(
            id=1,
            data={
                "description": "Test Description \nTheme Song: Test Track - https://open.spotify.com/track/123"
            },
        )

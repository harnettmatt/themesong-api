from datetime import datetime

from strava.models import StravaUserInfo
from strava.schemas import StravaAthlete, StravaTokenResponse
from user.models import User


def test_authorization(test_client, mocker, local_session):
    """
    Test that the authorization endpoint returns a 200 status code
    """
    # Arrange
    strava_token_response = StravaTokenResponse(
        access_token="123",
        refresh_token="123",
        expires_at=datetime(2023, 7, 9, 0, 0, 0, 0),
        athlete=StravaAthlete(
            id=123,
            username="test",
            firstname="test",
            lastname="test",
        ),
    )
    mocker.patch(
        "strava.router.StravaAPIService.exchange_code",
        return_value=strava_token_response,
    )
    # Act
    response = test_client.get(
        "/strava/authorization?code=123&scope=activity:read_all,activity:write"
    )
    # Assert
    assert response.status_code == 200

    user = local_session.query(User).get(123)
    assert user is not None
    assert user.id == 123

    strava_user_info = local_session.query(StravaUserInfo).get(123)
    assert strava_user_info is not None
    assert strava_user_info.id == 123
    assert strava_user_info.user_id == 123
    assert strava_user_info.access_token == "123"
    assert strava_user_info.refresh_token == "123"
    assert strava_user_info.expires_at == datetime(2023, 7, 9, 0, 0, 0, 0).strftime(
        "%Y-%m-%dT%H:%M:%S"
    )

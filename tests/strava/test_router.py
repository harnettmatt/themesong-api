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


def test_verify_webook(test_client, mocker):
    """
    Test that the verify webhook endpoint returns a 200 status code
    """
    # Arrange
    mocker.patch("strava.router.ENV_VARS.STRAVA_WEBHOOK_TOKEN", "123")
    # Act
    response = test_client.get(
        "/strava/webhook?hub.mode=subscribe&hub.verify_token=123&hub.challenge=456"
    )
    # Assert
    assert response.status_code == 200
    assert response.json() == {"hub.challenge": "456"}


def test_verify_webhook_403(test_client):
    # Arrange
    # Act
    response = test_client.get(
        "/strava/webhook?hub.mode=other&hub.verify_token=123&hub.challenge=456"
    )
    # Assert
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}

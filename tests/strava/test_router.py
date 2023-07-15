from datetime import datetime

from spotify.client import SpotifyAPIService
from spotify.models import SpotifyUserInfo
from spotify.schemas import (
    SpotifyPlayHistoryObject,
    SpotifyRecentlyPlayedResponse,
    SpotifyTrack,
)
from strava import schemas
from strava.client import StravaAPIService
from strava.models import StravaAuthStateParam, StravaUserInfo
from strava.schemas import StravaAthlete, StravaTokenResponse
from user.models import User


# FIXME: test is missing state functionality
def test_authorization(test_client, mocker, local_session):
    """
    Test that the authorization endpoint returns a 200 status code
    """
    # Arrange
    local_session.add(StravaAuthStateParam(id="123"))
    local_session.commit()
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
        "/strava/authorization?code=123&scope=activity:read_all,activity:write&state=123"
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


def test_authorization_403(test_client):
    # Arrange
    # Act
    response = test_client.get(
        "/strava/authorization?code=123&scope=activity:read_all,activity:write&state=123"
    )
    # Assert
    assert response.status_code == 403
    assert response.json() == {"detail": "Access Denied"}


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


def test_receive_event(test_client, mocker, local_session):
    """
    Test that the receive event endpoint returns a 200 status code
    """
    # Arrange
    # seed users in db
    user = User(id=123)
    strava_user_info = StravaUserInfo(
        id=123,
        user_id=123,
        access_token="123",
        refresh_token="123",
        expires_at=datetime(2023, 7, 9, 0, 0, 0, 0).strftime("%Y-%m-%dT%H:%M:%S"),
    )
    spotify_user_info = SpotifyUserInfo(
        id=123,
        user_id=123,
        access_token="123",
        refresh_token="123",
        expires_in=3600,
    )
    local_session.add_all([user, strava_user_info, spotify_user_info])
    local_session.commit()
    # mock strava api service
    strava_activity = schemas.StravaActivity(
        id=123,
        start_date=datetime(2021, 7, 9, 0, 0, 0, 0),
        description="",
    )
    mocker.patch.object(
        StravaAPIService,
        StravaAPIService.get_activity.__name__,
        return_value=strava_activity,
    )
    strava_activity_stream = schemas.StravaActivityStream(
        heartrate=schemas.StravaActivityStreamData(data=[1, 2, 3]),
        time=schemas.StravaActivityStreamData(data=[1, 2, 3]),
    )
    mocker.patch.object(
        StravaAPIService,
        StravaAPIService.get_stream_for_activity.__name__,
        return_value=strava_activity_stream,
    )
    mocker.patch.object(StravaAPIService, StravaAPIService.update_activity.__name__)
    # mock spotify api service
    recently_played = SpotifyRecentlyPlayedResponse(
        next="",
        items=[
            SpotifyPlayHistoryObject(
                played_at=datetime(2021, 7, 9, 0, 0, 5, 0),
                track=SpotifyTrack(
                    id="123", name="test", duration_ms=10000, href="test"
                ),
            )
        ],
    )
    mocker.patch.object(
        SpotifyAPIService,
        SpotifyAPIService.get_recenty_played.__name__,
        return_value=recently_played,
    )
    # Act
    response = test_client.post(
        "/strava/webhook",
        json={
            "aspect_type": "create",
            "object_id": 123,
            "object_type": "activity",
            "owner_id": 123,
        },
    )
    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "id": "123",
        "name": "test",
        "duration_ms": 10000,
        "href": "test",
    }

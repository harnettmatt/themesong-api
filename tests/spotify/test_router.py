from datetime import timedelta

from app.spotify.models import SpotifyAuthStateParam, SpotifyUserInfo
from app.spotify.schemas import SpotifyTokenResponse, SpotifyUserResponse
from app.user.models import User


def test_login(test_client, mocker, local_session):
    # Arrange
    mocker.patch("app.spotify.router.generate_auth_state", return_value="123")
    # Act
    response = test_client.get("/spotify/login?user_id=456")
    # Assert
    assert (
        response.request.url
        == "https://accounts.spotify.com/authorize?response_type=code&client_id=0987654321&redirect_uri=https%3A%2F%2F123abctest.com%2Fspotify%2Fauthorization&scope=user-read-private+user-read-email+user-read-recently-played&state=123"
    )
    assert local_session.query(SpotifyAuthStateParam).get(
        "123"
    ) == SpotifyAuthStateParam(id="123", user_id=456)


def test_authorization(test_client, mocker, local_session):
    """
    Test that the authorization endpoint returns a 200 status code
    """
    # Arrange
    local_session.add(User(id=123))
    local_session.add(SpotifyAuthStateParam(id="456", user_id=123))
    local_session.commit()
    spotify_token_response = SpotifyTokenResponse(
        access_token="789",
        refresh_token="abc",
        expires_in=timedelta(seconds=3600),
    )
    mocker.patch(
        "app.spotify.router.SpotifyAPIService.exchange_code",
        return_value=spotify_token_response,
    )
    mocker.patch(
        "app.spotify.router.SpotifyAPIService.get_user",
        return_value=SpotifyUserResponse(id="def"),
    )
    # Act
    response = test_client.get(
        "/spotify/authorization?code=123&scope=activity:read_all,activity:write&state=456",
        allow_redirects=False,
    )
    # Assert
    assert response.status_code == 307
    assert response.headers["Location"] == "http://localhost:5173/spotify/def"

    spotify_user_info = local_session.query(SpotifyUserInfo).get("def")
    assert spotify_user_info is not None
    assert spotify_user_info.id == "def"
    assert spotify_user_info.user_id == 123
    assert local_session.query(SpotifyAuthStateParam).get("456") is None


def test_authorization_403(test_client):
    # Act
    response = test_client.get(
        "/spotify/authorization?code=123&scope=activity:read_all,activity:write&state=456"
    )
    # Assert
    assert response.status_code == 403
    assert response.json() == {"detail": "Access Denied"}

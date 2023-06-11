import pytest
import requests

from auth.utils import get_config, get_current_user_id, verify_token


@pytest.fixture(name="access_token")
def get_access_token():
    config = get_config()
    response = requests.post(
        url=f'https://{config["DOMAIN"]}/oauth/token',
        headers={"content-type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "password",
            "username": config["TEST_USERNAME"],
            "password": config["TEST_PASSWORD"],
            "client_id": config["CLIENT_ID"],
            "client_secret": config["CLIENT_SECRET"],
            "audience": config["API_AUDIENCE"],
        },
    )
    assert response.status_code == 200
    return response.json().get("access_token")


class TestUtils:
    @staticmethod
    def test_verify_token(access_token):
        config = get_config()

        # unit under test
        response = verify_token(token=access_token, config=config)

        assert response.get("error") is None

    @staticmethod
    def test_get_current_user(access_token):
        config = get_config()

        # unit under test
        user_id = get_current_user_id(token=access_token, config=config)

        # user id for test@example.com in Auth0
        assert user_id == config["TEST_USER_ID"]

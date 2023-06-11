"""Unit tests for /users routing handler"""
import pytest
from fastapi.encoders import jsonable_encoder

from conftest import override_get_session
from user import handler, models


class TestHandler:
    """Unit tests for /users routing handler"""

    @staticmethod
    @pytest.mark.integtest
    def test_get_all(test_client, mock_random_user):
        """
        GIVEN: a GET request to /users
        THEN: a list of Users is returned
        """
        response = test_client.get("/users/")

        assert response.status_code == 200
        assert jsonable_encoder(mock_random_user) in response.json()

    @staticmethod
    @pytest.mark.integtest
    def test_get(test_client, mock_random_user):
        """
        GIVEN: a GET request to /users/{id}
        THEN: the corresponding user is returned
        """
        # unit under test
        response = test_client.get(f"/users/{mock_random_user.id}")

        assert response.status_code == 200
        assert jsonable_encoder(mock_random_user) == response.json()

    @staticmethod
    @pytest.mark.integtest
    def test_get_404(test_client):
        """
        GIVEN: a GET request to /users/{id}
        WHEN: the user does not exist
        THEN: a 404 error is returned
        """
        # unit under test
        response = test_client.get(f"/users/{9999999}")

        assert response.status_code == 404

    @staticmethod
    @pytest.mark.integtest
    def test_create(mock_random_user_id):
        """
        NOTE: this test is invoking the handler directly because it is easier
              to use dependency injection for the user id which is override
              the global override

        GIVEN: a request to create() user handler
        THEN: a User is created and returned
        """

        response = handler.create(
            session=next(override_get_session()), user_id=mock_random_user_id
        )

        assert response == models.User(id=mock_random_user_id)

    @staticmethod
    @pytest.mark.integtest
    def test_delete(test_client, mock_random_user):
        """
        GIVEN: a DELETE request to /users/{id}
        THEN: the corresponding user is returned
        """
        # unit under test
        response = test_client.delete(f"/users/{mock_random_user.id}")

        assert response.status_code == 200
        assert jsonable_encoder(mock_random_user) == response.json()

        response = test_client.get(f"users/{mock_random_user.id}")

        assert response.status_code == 404

    @staticmethod
    @pytest.mark.integtest
    def test_delete_404(test_client):
        """
        GIVEN: a DELETE request to /users/{id}
        WHEN: the user does not exist
        THEN: a 404 error is returned
        """
        # unit under test
        response = test_client.delete(f"/users/{9999999}")

        assert response.status_code == 404

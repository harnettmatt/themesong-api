"""Unit tests for /groups routing handler"""
import pytest
from fastapi.encoders import jsonable_encoder

from group import schemas


class TestHandler:
    """Unit tests for /groups routing handler"""

    @staticmethod
    @pytest.mark.integtest
    def test_get_all(test_client, mock_group):
        """
        GIVEN: a GET request to /groups
        THEN: a list of Groups is returned
        """
        response = test_client.get("/groups/")

        expected_group = schemas.Group(**jsonable_encoder(mock_group))
        assert response.status_code == 200
        assert expected_group in response.json()

    @staticmethod
    @pytest.mark.integtest
    def test_get(test_client, mock_group):
        """
        GIVEN: a GET request to /groups/{id}
        THEN: the corresponding group is returned
        """
        # unit under test
        response = test_client.get(f"/groups/{mock_group.id}")

        expected_group = schemas.Group(**jsonable_encoder(mock_group))
        assert response.status_code == 200
        assert expected_group == response.json()

    @staticmethod
    @pytest.mark.integtest
    def test_create(test_client):
        """
        GIVEN: a POST request to /groups with a request body
        THEN: a Group is created and returned
        """
        request_body = {"name": "Ramen"}

        # unit under test
        response = test_client.post("/groups/", json=request_body)

        assert response.status_code == 200
        response_dict = response.json()
        assert "id" in response_dict
        del response_dict["id"]
        assert response_dict == {"name": "Ramen", "items": []}

    @staticmethod
    @pytest.mark.integtest
    def test_patch(test_client, mock_group):
        """
        GIVEN: a PATCH request to /groups with a request body
        THEN: a Group is updated and returned
        """

        request_body = {"name": "NY Ramen"}
        expected_group = schemas.Group(id=mock_group.id, **request_body)

        # unit under test
        response = test_client.patch(f"/groups/{mock_group.id}", json=request_body)

        assert response.status_code == 200
        assert response.json() == expected_group

        response = test_client.get(f"/groups/{expected_group.id}")

        assert response.status_code == 200
        assert response.json() == expected_group

    @staticmethod
    @pytest.mark.integtest
    def test_delete(test_client, mock_group):
        """
        GIVEN: a DELETE request to /groups/{id}
        THEN: the corresponding group is returned
        """
        expected_group = schemas.Group(**jsonable_encoder(mock_group))

        # unit under test
        response = test_client.delete(f"/groups/{mock_group.id}")

        assert response.status_code == 200
        assert expected_group == response.json()

        response = test_client.get(f"groups/{mock_group.id}")

        assert response.status_code == 404

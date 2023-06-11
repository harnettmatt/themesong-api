"""Unit tests for /items routing handler"""
import pytest
from fastapi.encoders import jsonable_encoder

from item import schemas


class TestHandler:
    """Unit tests for /items routing handler"""

    @staticmethod
    @pytest.mark.integtest
    def test_get_all(test_client, mock_item):
        """
        GIVEN: a GET request to /items
        THEN: a list of Items is returned
        """
        response = test_client.get("/items/")

        expected_item = schemas.Item(**jsonable_encoder(mock_item))
        assert response.status_code == 200
        assert expected_item in response.json()

    @staticmethod
    @pytest.mark.integtest
    def test_get(test_client, mock_item):
        """
        GIVEN: a GET request to /items/{id}
        THEN: the corresponding item is returned
        """
        # unit under test
        response = test_client.get(f"/items/{mock_item.id}")

        expected_item = schemas.Item(**jsonable_encoder(mock_item))
        assert response.status_code == 200
        assert expected_item == response.json()

    @staticmethod
    @pytest.mark.integtest
    def test_create(test_client):
        """
        GIVEN: a POST request to /items with a request body
        THEN: a Item is created and returned
        """
        request_body = {"name": "Minca"}

        # unit under test
        response = test_client.post("/items/", json=request_body)

        assert response.status_code == 200
        response_dict = response.json()
        assert "id" in response_dict
        del response_dict["id"]
        assert response_dict == {"name": "Minca"}

    @staticmethod
    @pytest.mark.integtest
    def test_patch(test_client, mock_item):
        """
        GIVEN: a PATCH request to /items with a request body
        THEN: a Item is updated and returned
        """

        request_body = {"name": "New Name"}
        expected_item = schemas.Item(id=mock_item.id, **request_body)

        # unit under test
        response = test_client.patch(f"/items/{mock_item.id}", json=request_body)

        assert response.status_code == 200
        assert response.json() == expected_item

        response = test_client.get(f"/items/{expected_item.id}")

        assert response.status_code == 200
        assert response.json() == expected_item

    @staticmethod
    @pytest.mark.integtest
    def test_delete(test_client, mock_item):
        """
        GIVEN: a DELETE request to /items/{id}
        THEN: the corresponding item is returned
        """
        expected_item = schemas.Item(**jsonable_encoder(mock_item))

        # unit under test
        response = test_client.delete(f"/items/{mock_item.id}")

        assert response.status_code == 200
        assert expected_item == response.json()

        response = test_client.get(f"items/{mock_item.id}")

        assert response.status_code == 404

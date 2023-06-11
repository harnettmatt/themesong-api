"""Unit tests for /memberships routing handler"""

import pytest
from fastapi.encoders import jsonable_encoder


class TestHandler:
    """Unit tests for /memberships routing handler"""

    @staticmethod
    @pytest.mark.integtest
    def test_get_all(test_client, mock_membership):
        """
        GIVEN: a GET request to /memberships
        THEN:
            - a list of memberhips is returned
            - the item is associated with the group
        """
        response = test_client.get("/memberships/")

        assert response.status_code == 200
        assert jsonable_encoder(mock_membership) in response.json()

    @staticmethod
    @pytest.mark.integtest
    def test_get(test_client, mock_membership):
        """
        GIVEN: a GET request to /memberships/{id}
        THEN: the corresponding membership is returned
        """
        # unit under test
        response = test_client.get(f"/memberships/{mock_membership.id}")

        assert response.status_code == 200
        assert jsonable_encoder(mock_membership) == response.json()

    @staticmethod
    @pytest.mark.integtest
    def test_get_404(test_client, mock_membership):
        """
        GIVEN: a GET request to /memberships/{id}
        WHEN: the membership does not exist
        THEN: a 404 error is returned
        """
        # unit under test
        response = test_client.get(f"/memberships/{9999999}")

        assert response.status_code == 404

    @staticmethod
    @pytest.mark.integtest
    def test_create(test_client, mock_group, mock_item):
        """
        GIVEN: a POST request to /memberships with a request body
        THEN: a Membership is created and returned
        """

        request_body = {"group_id": mock_group.id, "item_id": mock_item.id}

        # unit under test
        response = test_client.post("/memberships/", json=request_body)

        assert response.status_code == 200
        response_dict = response.json()
        assert "id" in response_dict
        del response_dict["id"]
        assert response_dict == request_body

        groups_response = test_client.get(f"/groups/{mock_group.id}")
        items_response = test_client.get(f"/items/{mock_item.id}")

        assert groups_response.status_code == 200
        assert items_response.status_code == 200
        assert items_response.json() in groups_response.json().get("items")

    @staticmethod
    @pytest.mark.integtest
    def test_delete(test_client, mock_membership):
        """
        GIVEN: a DELETE request to /memberships/{id}
        THEN:
            - the corresponding membership is returned
            - a subsequent GET returns 404
            - and the item is disassociated from the corresponding group
        """
        # unit under test
        response = test_client.delete(f"/memberships/{mock_membership.id}")

        assert response.status_code == 200
        assert jsonable_encoder(mock_membership) == response.json()

        response = test_client.get(f"memberships/{mock_membership.id}")

        assert response.status_code == 404

        groups_response = test_client.get(f"/groups/{mock_membership.group_id}")
        items_response = test_client.get(f"/items/{mock_membership.item_id}")

        assert groups_response.status_code == 200
        assert items_response.status_code == 200
        assert items_response.json() not in groups_response.json().get("items")

    @staticmethod
    @pytest.mark.integtest
    def test_delete_404(test_client):
        """
        GIVEN: a DELETE request to /memberships/{id}
        WHEN: the membership does not exist
        THEN: a 404 error is returned
        """
        # unit under test
        response = test_client.delete(f"/memberships/{9999999}")

        assert response.status_code == 404

import pytest

from app.api_utils.schemas import APITokenRequest


def test_api_token_request_validate_grant_type_refresh_token():
    # Arrange
    # Act
    request = APITokenRequest(refresh_token="token")
    # Assert
    assert request.refresh_token == "token"
    assert request.code is None
    assert request.grant_type == "refresh_token"


def test_api_token_request_validate_grant_type_token_code():
    # Arrange
    # Act
    request = APITokenRequest(code="code")
    # Assert
    assert request.refresh_token is None
    assert request.code == "code"
    assert request.grant_type == "authorization_code"


def test_api_token_request_validate_code_or_refresh_token_both():
    # Arrange
    # Act
    with pytest.raises(ValueError):
        APITokenRequest(refresh_token="token", code="code")
    # Assert


def test_api_token_request_validate_code_or_refresh_token_neither():
    # Arrange
    # Act
    with pytest.raises(ValueError):
        APITokenRequest()
    # Assert

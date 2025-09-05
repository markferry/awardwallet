import json
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from awardwallet.api import (
    AuthenticationError,
    AwardWalletAPIError,
    AwardWalletClient,
    NotFoundError,
)
from awardwallet.model import (
    AccessLevel,
    ConnectedUserListItem,
    GetAccountDetailsResponse,
    GetConnectedUserDetailsResponse,
    ProviderInfo,
    ProviderKind,
    TypedHistoryValue,
)

DUMMY_API_KEY = "test_api_key"


@pytest.fixture
def api_client():
    """Provides a fresh instance of the AwardWalletClient client for each test."""
    return AwardWalletClient(api_key=DUMMY_API_KEY)


# Use with indirect parametrization
# e.g.  @pytest.mark.parametrize("test_data", [["file1.json"]], indirect=True)
@pytest.fixture
def test_data(request):
    """Loads JSON test data from a specified file."""
    with open(request.param) as f:
        return json.load(f)


def mock_api_call(mocker, status_code=200, json_response=None, text_response=""):
    """A helper function to mock the requests session call."""
    mock_response = Mock()
    mock_response.status_code = status_code

    if json_response is not None:
        mock_response.json.return_value = json_response
    else:
        # If no JSON, make the .json() call raise an error, just like requests would
        mock_response.json.side_effect = ValueError("No JSON object could be decoded")
        mock_response.text = text_response

    # The target to patch is the `request` method within the `requests.Session`
    # instance used by our API client.
    mocker.patch("requests.Session.request", return_value=mock_response)


class TestListMethods:
    def test_list_providers_success(self, mocker, api_client):
        """Tests successful retrieval and parsing of the providers list."""
        # Arrange
        mock_response_data = [
            {"code": "aa", "displayName": "American Airlines (AAdvantage)", "kind": 1},
            {"code": "marriott", "displayName": "Marriott (Bonvoy)", "kind": 2},
        ]
        mock_api_call(mocker, json_response=mock_response_data)

        # Act
        providers = api_client.list_providers()

        # Assert
        assert len(providers) == 2
        assert all(isinstance(p, ProviderInfo) for p in providers)
        assert providers[0].code == "aa"
        assert providers[0].kind == ProviderKind.AIRLINE
        assert providers[1].display_name == "Marriott (Bonvoy)"
        assert providers[1].kind == ProviderKind.HOTEL

    @pytest.mark.parametrize(
        "test_data", ["tests/data/connected_users.json"], indirect=True
    )
    def test_list_connected_users_success(self, mocker, api_client, test_data):
        """Tests successful retrieval and parsing of the connected_users list."""
        # Arrange
        mock_response_data = test_data
        mock_api_call(mocker, json_response=mock_response_data)

        # Act
        connected_users = api_client.list_connected_users()

        # Assert
        assert len(connected_users) == 1
        assert all(isinstance(u, ConnectedUserListItem) for u in connected_users)
        assert connected_users[0].user_id == 123456
        assert connected_users[0].email == "testuser@example.com"

    def test_list_members_empty(self, mocker, api_client):
        """Tests handling of an empty list response from the API."""
        # Arrange
        mock_response_data = {"members": []}
        mock_api_call(mocker, json_response=mock_response_data)

        # Act
        members = api_client.list_members()

        # Assert
        assert members == []


# --- Tests for Get Details Methods ---


class TestGetDetailsMethods:
    @pytest.mark.parametrize(
        "test_data", ["tests/data/user_details.json"], indirect=True
    )
    def test_get_connected_user_details(self, mocker, api_client, test_data):
        """Tests successful retrieval and parsing of a detailed object."""
        # Arrange
        user_id = 12345
        mock_response_data = test_data
        mock_api_call(mocker, json_response=mock_response_data)

        # Act
        details = api_client.get_connected_user_details(user_id)

        # Assert
        assert isinstance(details, GetConnectedUserDetailsResponse)
        assert details.user_id == user_id
        assert details.full_name == "John Smith"
        assert len(details.accounts) == 1
        assert details.accounts[0].account_id == 7654321

    @pytest.mark.parametrize(
        "test_data", ["tests/data/account_details.json"], indirect=True
    )
    def test_get_account_details(self, mocker, api_client, test_data):
        # Arrange
        account_id = 7654321
        mock_response_data = test_data
        mock_api_call(mocker, json_response=mock_response_data)

        # Act
        details = api_client.get_account_details(account_id)

        # Assert
        assert isinstance(details, GetAccountDetailsResponse)
        assert details.account.account_id == account_id

    @pytest.mark.parametrize(
        "test_data", ["tests/data/user_details.json"], indirect=True
    )
    def test_get_connected_user_details_with_typed_history(
        self, mocker, api_client, test_data
    ):
        """UPDATED: Verifies that history values are normalized and correctly typed."""
        # Arrange
        user_id = test_data["userId"]
        mock_api_call(mocker, json_response=test_data)

        # Act
        details = api_client.get_connected_user_details(user_id)

        # Assert
        assert isinstance(details, GetConnectedUserDetailsResponse)
        account = details.accounts[0]

        field_date = account.history[0].fields[0]  # pyright: ignore
        assert field_date.name == "Transaction Date"
        assert isinstance(field_date.value, TypedHistoryValue)
        assert isinstance(field_date.value.value, str)
        assert field_date.value.type == "string"

        field_points = account.history[0].fields[3]  # pyright: ignore
        assert field_points.name == "Points"
        assert isinstance(field_points.value, TypedHistoryValue)
        assert field_points.value.value == -100
        assert isinstance(field_points.value.value, int)
        assert field_points.value.type == "miles"

        # old-style is returned as str
        field_points = account.history[1].fields[3]  # pyright: ignore
        assert field_points.name == "Points"
        assert isinstance(field_points.value, TypedHistoryValue)
        assert field_points.value.value == "+100"

    def test_pydantic_validation_error(self, mocker, api_client):
        # Arrange
        # 'kind' is required, so we remove it from the mock response
        malformed_response = {"code": "badjet", "displayName": "BadJet Rewards"}
        mock_api_call(mocker, json_response=malformed_response)

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            api_client.get_provider_info("badjet")

        # Check that the error message is helpful
        assert "Field required" in str(exc_info.value)
        assert "kind" in str(exc_info.value)


class TestPostMethods:
    def test_get_connection_link(self, mocker, api_client):
        # Arrange
        expected_url = "https://awardwallet.com/user/connections/approve?..."
        mock_response_data = {"url": expected_url}
        # We need to get the patched method to check how it was called
        patched_request = mocker.patch(
            "requests.Session.request",
            return_value=Mock(status_code=200, json=lambda: mock_response_data),
        )

        # Act
        url = api_client.get_connection_link(
            platform="desktop",
            access_level=AccessLevel.READ_BALANCES_AND_STATUS,
            state="my-state-123",
        )

        # Assert
        assert url == expected_url

        # Verify that the underlying request was made correctly
        patched_request.assert_called_once()
        call_args, call_kwargs = patched_request.call_args
        assert call_args[0] == "POST"  # Method
        assert call_args[1].endswith("/create-auth-url")  # URL
        assert call_kwargs["json"] == {
            "platform": "desktop",
            "access": 1,  # Correct integer value for the enum
            "state": "my-state-123",
            "granularSharing": False,
        }


class TestErrorHandling:
    def test_authentication_error_401(self, mocker, api_client):
        """Tests that a 401 response raises AuthenticationError."""
        # Arrange
        mock_api_call(
            mocker, status_code=401, json_response={"error": "Invalid API Key"}
        )

        # Act & Assert
        with pytest.raises(AuthenticationError) as exc_info:
            api_client.list_providers()
        assert "Invalid API Key" in str(exc_info.value)
        assert exc_info.value.status_code == 401

    def test_not_found_error_404(self, mocker, api_client):
        """Tests that a 404 response raises NotFoundError."""
        # Arrange
        mock_api_call(
            mocker, status_code=404, json_response={"error": "Member not found"}
        )

        # Act & Assert
        with pytest.raises(NotFoundError):
            api_client.get_member_details(9999)

    def test_server_error_500(self, mocker, api_client):
        """Tests that a 500 response raises a generic AwardWalletAPIError."""
        # Arrange
        mock_api_call(mocker, status_code=500, text_response="Internal Server Error")

        # Act & Assert
        with pytest.raises(AwardWalletAPIError) as exc_info:
            api_client.list_providers()
        assert "Internal Server Error" in str(exc_info.value)
        assert exc_info.value.status_code == 500

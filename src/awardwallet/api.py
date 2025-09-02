# awardwallet_api.py

from enum import IntEnum
from typing import Any

import requests

# --- Custom Exceptions for Better Error Handling ---


class AwardWalletAPIError(Exception):
    """Base exception for all AwardWallet API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(f"Status {status_code}: {message}" if status_code else message)


class AuthenticationError(AwardWalletAPIError):
    """Raised for 401 Unauthorized errors."""

    pass


class ForbiddenError(AwardWalletAPIError):
    """Raised for 403 Forbidden errors."""

    pass


class NotFoundError(AwardWalletAPIError):
    """Raised for 404 Not Found errors."""

    pass


# --- Helper Enum for Access Levels ---


class AccessLevel(IntEnum):
    """
    Identifies the level of account access to be granted by the user.
    """

    READ_NUMBERS_AND_STATUS = 0
    READ_BALANCES_AND_STATUS = 1
    READ_ALL_EXCEPT_PASSWORDS = 2
    FULL_CONTROL = 3


class ProviderKind(IntEnum):
    """
    Type of Provider
    """

    AIRLINE = 1
    HOTEL = 2
    CAR_RENTAL = 3
    TRAIN = 4
    OTHER = 5
    CREDIT_CARD = 6
    SHOPPING = 7
    DINING = 8
    SURVEY = 9
    CRUISE_LINE = 10
    PARKING = 12


class AwardWalletClient:
    """
    A Python wrapper for the AwardWallet Account Access API.

    This client requires a Business Account with AwardWallet. The API key can be
    found in your business account settings.

    https://awardwallet.com/api/account#introduction
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://business.awardwallet.com/api/export/v1",
    ):
        """
        Initializes the AwardWallet client.

        Args:
            api_key (str): Your AwardWallet Business API key.
            base_url (str, optional): The base URL of the API.
        """
        if not api_key:
            raise ValueError("API key cannot be empty.")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()
        # Per documentation, authentication is done via the 'X-Authentication' header
        self._session.headers.update(
            {
                "X-Authentication": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """
        A private helper method to make authenticated API requests.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self._session.request(method, url, **kwargs)

            if 400 <= response.status_code < 600:
                try:
                    error_data = response.json()
                    message = error_data.get("error", response.text)
                except requests.exceptions.JSONDecodeError:
                    message = response.text

                if response.status_code == 401:
                    raise AuthenticationError(message, response.status_code)
                if response.status_code == 403:
                    raise ForbiddenError(message, response.status_code)
                if response.status_code == 404:
                    raise NotFoundError(message, response.status_code)

                raise AwardWalletAPIError(message, response.status_code)

            # Handle 204 No Content response
            if response.status_code == 204:
                return None

            return response.json()

        except requests.exceptions.RequestException as e:
            raise AwardWalletAPIError(f"A connection error occurred: {e}") from e

    # --- Connect Endpoints ---

    def get_connection_link(
        self,
        platform: str,
        access_level: AccessLevel,
        state: str | None = None,
        granular_sharing: bool = False,
    ) -> str:
        """
        Gets a unique URL to connect an AwardWallet user to your business
        account.

        See: https://awardwallet.com/api/account#method-Connect_1

        Args:
            platform (str): 'mobile' or 'desktop'.
            access_level (AccessLevel):
                - 0 Read account numbers / usernames and elite statuses only
                - 1 Read account balances and elite statuses only
                - 2 Read all information excluding passwords
                - 3 Full control (edit, delete, auto-login, view passwords)

            state (str, optional): A string to maintain state between your
            request and the callback.

            granular_sharing (bool, optional): If true, allows users to select
            which accounts to share. Defaults to False.

        Returns:
            str: The connection URL to which you should redirect your user.
        """
        payload = {
            "platform": platform,
            "access": int(access_level),
            "state": state,
            "granularSharing": granular_sharing,
        }
        response = self._request("POST", "create-auth-url", json=payload)
        return response.get("url")

    def get_connected_user_info_from_code(self, code: str) -> dict[str, Any]:
        """
        After a successful connection, use the code from the redirect to get
        the new user's ID.

        Args:
            code (str): The code received as a GET parameter in your redirect URI.

        Returns:
            Dict[str, Any]: A dictionary containing the 'userId'.
        """
        return self._request("GET", f"get-connection-info/{code}")

    # --- Accounts Endpoint ---

    def get_account_details(self, account_id: int) -> dict[str, Any]:
        """
        Gets comprehensive details for a specific loyalty account, including
        transaction history.

        Args:
            account_id (int): The unique ID of the account.

        Returns:
            Dict[str, Any]: A dictionary containing the detailed account information.
        """
        return self._request("GET", f"account/{account_id}")

    # --- Members Endpoints (Profiles managed within your business account) ---

    def list_members(self) -> list[dict[str, Any]]:
        """
        Retrieves all 'Members' under your business account. Members are profiles
        you create and are not linked to a personal AwardWallet account.

        Returns:
            List[Dict[str, Any]]: A list of member objects.
        """
        response = self._request("GET", "member")
        return response.get("members", [])

    def get_member_details(self, member_id: int) -> dict[str, Any]:
        """
        Retrieves all loyalty accounts and details for a specific Member.

        Args:
            member_id (int): The unique ID of the Member.

        Returns:
            Dict[str, Any]: A dictionary containing member details and list of accounts.
        """
        return self._request("GET", f"member/{member_id}")

    # --- Connected Users Endpoints (Users with their own AwardWallet account) ---

    def list_connected_users(self) -> list[dict[str, Any]]:
        """
        Retrieves all users who have connected their personal AwardWallet
        account to your business account.

        Returns:
            List[Dict[str, Any]]: A list of connected user objects.
        """
        response = self._request("GET", "connectedUser")
        return response.get("connectedUsers", [])

    def get_connected_user_details(self, user_id: int) -> dict[str, Any]:
        """
        Retrieves details and shared loyalty accounts for a specific Connected User.

        Args:
            user_id (int): The unique ID of the Connected User.

        Returns:
            Dict[str, Any]: A dictionary containing user details and a list of
            their shared accounts.
        """
        return self._request("GET", f"connectedUser/{user_id}")

    # --- Providers Endpoints ---

    def list_providers(self) -> list[dict[str, Any]]:
        """
        Retrieves the list of all loyalty program providers supported by AwardWallet.

        Returns:
            List[Dict[str, Any]]: A list of provider information.
        """
        return self._request("GET", "providers/list")

    def get_provider_info(self, provider_code: str) -> dict[str, Any]:
        """
        Retrieves detailed information about a specific provider, including required
        login fields and supported features.

        Args:
            provider_code (str): The unique code for the provider (e.g., 'aa').

        Returns:
            Dict[str, Any]: Detailed information about the provider.
        """
        return self._request("GET", f"providers/{provider_code}")

from __future__ import annotations

from datetime import datetime
from enum import IntEnum
from typing import Any, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from pydantic.alias_generators import to_camel

CONFIG = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class AccessLevel(IntEnum):
    """Identifies the level of account access to be granted by the user."""

    READ_NUMBERS_AND_STATUS = 0
    READ_BALANCES_AND_STATUS = 1
    READ_ALL_EXCEPT_PASSWORDS = 2
    FULL_CONTROL = 3


class AccountProperty(BaseModel):
    """A secondary attribute of a loyalty account."""

    model_config = CONFIG

    name: str
    value: str
    rank: Optional[int] = None
    kind: Optional[int] = None


class TypedHistoryValue(BaseModel):
    """
    Represents the nested value object in a history field.
    It automatically converts its 'value' to the correct Python type.
    """

    type: str
    value: Any  # Start with 'Any' and let the validator assign the correct type

    @model_validator(mode="before")
    @classmethod
    def convert_value_based_on_type(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Reads the 'type' field and attempts to cast the 'value' field
        to the appropriate Python type before validation continues.
        """
        if not isinstance(data, dict):
            return data  # Should not happen with our setup, but safe to have

        type_str = data.get("type")
        raw_value = data.get("value")

        if raw_value is None:
            return data

        converted_value = raw_value
        try:
            if type_str in ("miles", "points"):
                # Remove commas and convert to integer
                converted_value = int(str(raw_value).replace(",", ""))
            # Add more type conversions here as they are discovered
            # For example:
            # elif type_str == "date":
            #     converted_value = datetime.strptime(raw_value, "%m/%d/%y").date()
        except (ValueError, TypeError):
            # If conversion fails, leave it as a string
            converted_value = str(raw_value)

        data["value"] = converted_value
        return data


class HistoryField(BaseModel):
    """
    A single field within a transaction history entry.
    Ensures its 'value' is always a TypedHistoryValue object.
    """

    model_config = CONFIG

    code: str
    name: str
    value: TypedHistoryValue

    # runs BEFORE standard validation. It ensures that if the API
    # sends a simple string, we wrap it into the required object structure.
    @field_validator("value", mode="before")
    @classmethod
    def ensure_value_is_object(cls, v: Any) -> dict[str, Any]:
        """If the incoming value is a simple string, wrap it in the object structure."""
        if isinstance(v, str):
            return {"value": v, "type": "string"}
        return v


class HistoryItem(BaseModel):
    """A single transaction history entry."""

    model_config = CONFIG

    fields: Optional[list[HistoryField]] = []


class SubAccount(BaseModel):
    """Represents a sub-account, like an individual card under a bank account."""

    model_config = CONFIG

    sub_account_id: int
    display_name: str
    balance: str
    balance_raw: Optional[float] = None
    last_detected_change: Optional[str] = None
    properties: Optional[list[AccountProperty]] = []
    history: Optional[list[HistoryItem]] = []


class Account(BaseModel):
    """A full loyalty account object with all its details."""

    model_config = CONFIG

    account_id: int
    code: str
    display_name: str
    kind: str
    login: str
    autologin_url: str
    update_url: str
    edit_url: str
    balance: str
    balance_raw: float
    owner: str
    error_code: int
    last_detected_change: Optional[str] = None
    expiration_date: Optional[datetime] = None
    last_retrieve_date: Optional[datetime] = None
    last_change_date: Optional[datetime] = None
    error_message: Optional[str] = None
    properties: Optional[list[AccountProperty]] = []
    history: Optional[list[HistoryItem]] = []
    sub_accounts: Optional[list[SubAccount]] = []


class AccountsIndexItem(BaseModel):
    """A lightweight reference to an account, used in list views."""

    model_config = CONFIG

    account_id: int
    last_change_date: datetime
    last_retrieve_date: Optional[datetime] = None


class MemberListItem(BaseModel):
    """Represents a 'Member' in a list, with an index of their accounts."""

    model_config = CONFIG

    member_id: int
    full_name: str
    edit_member_url: str
    account_list_url: str
    timeline_url: str
    accounts_index: list[AccountsIndexItem]
    email: Optional[str] = None
    forwarding_email: Optional[str] = None


class GetMemberDetailsResponse(MemberListItem):
    """Full details for a single Member, including all their account objects."""

    model_config = CONFIG

    # This model inherits from MemberListItem but replaces the account index
    # with the full list of accounts.
    accounts: list[Account]
    accounts_index: Any = Field(None, exclude=True)  # Exclude the inherited field


class ConnectedUserListItem(BaseModel):
    """Represents a 'Connected User' in a list view."""

    model_config = CONFIG

    user_id: int
    full_name: str
    status: str
    user_name: str
    email: str
    forwarding_email: str
    connection_type: str
    accounts_access_level: str
    accounts_shared_by_default: bool
    edit_connection_url: str
    account_list_url: str
    timeline_url: str
    accounts_index: list[AccountsIndexItem]
    access_level: Optional[str] = None
    booking_requests_url: Optional[str] = None


class GetConnectedUserDetailsResponse(ConnectedUserListItem):
    """Full details for a single Connected User, including their shared accounts."""

    model_config = CONFIG

    accounts: list[Account]
    accounts_index: Any = Field(None, exclude=True)


class GetAccountDetailsResponse(BaseModel):
    """Response model for the get_account_details endpoint."""

    model_config = CONFIG

    account: list[Account]
    member: Optional[MemberListItem] = None
    connected_user: Optional[ConnectedUserListItem] = None


class ProviderKind(IntEnum):
    """Type of Provider"""

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


class ProviderInfo(BaseModel):
    """Information about a supported loyalty provider."""

    model_config = CONFIG

    code: str
    display_name: str
    kind: ProviderKind


class ProviderInputField(BaseModel):
    """Describes an input field required for a provider (e.g., login, password)."""

    model_config = CONFIG

    code: Optional[str] = None
    title: Optional[str] = None
    required: Optional[bool] = None
    default_value: Optional[str] = None


class ProviderPropertyInfo(BaseModel):
    """Describes a property or column for a provider."""

    model_config = CONFIG

    code: Optional[str] = None
    name: Optional[str] = None
    kind: Optional[str] = (
        None  # This 'kind' is a string in the API response for properties
    )


class ProviderDetails(BaseModel):
    """Detailed information about a single provider."""

    model_config = CONFIG

    kind: ProviderKind
    code: str
    display_name: str
    provider_name: Optional[str] = None
    program_name: Optional[str] = None
    login: Optional[ProviderInputField] = None
    login2: Optional[ProviderInputField] = None
    login3: Optional[ProviderInputField] = None
    password: Optional[ProviderInputField] = None
    properties: Optional[list[ProviderPropertyInfo]] = []
    history_columns: Optional[list[ProviderPropertyInfo]] = []
    auto_login: Optional[bool] = None
    can_parse_history: Optional[bool] = None
    can_check_itinerary: Optional[bool] = None
    can_check_confirmation: Optional[bool] = None

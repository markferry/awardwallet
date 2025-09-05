from __future__ import annotations

from datetime import datetime
from enum import IntEnum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field
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


class HistoryField(BaseModel):
    """A single field within a transaction history entry."""

    model_config = CONFIG

    code: str
    name: str
    value: str


class HistoryItem(BaseModel):
    """A single transaction history entry."""

    model_config = CONFIG

    fields: Optional[list[HistoryField]] = None


class SubAccount(BaseModel):
    """Represents a sub-account, like an individual card under a bank account."""

    model_config = CONFIG

    sub_account_id: int
    display_name: str
    balance: str
    balance_raw: Optional[float] = None
    last_detected_change: Optional[str] = None
    properties: Optional[list[AccountProperty]] = None
    history: Optional[list[HistoryItem]] = None


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
    properties: Optional[list[AccountProperty]] = None
    history: Optional[list[HistoryItem]] = None
    sub_accounts: Optional[list[SubAccount]] = None


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
    properties: Optional[list[ProviderPropertyInfo]] = None
    history_columns: Optional[list[ProviderPropertyInfo]] = None
    auto_login: Optional[bool] = None
    can_parse_history: Optional[bool] = None
    can_check_itinerary: Optional[bool] = None
    can_check_confirmation: Optional[bool] = None

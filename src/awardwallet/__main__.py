import json
import sys
from argparse import ArgumentParser
from typing import Any

from awardwallet import AwardWalletClient
from awardwallet.api import ProviderKind

from . import __version__

__all__ = ["main"]


def list_users(client):
    connected_users = client.list_connected_users()
    users = {}
    for user in connected_users:
        users[user["userId"]] = user["userName"]

    return users


def account_details(client, account_id):
    return client.get_account_details(account_id)


def user_details(client, user_id):
    return client.get_connected_user_details(user_id)


def list_providers(client):
    providers = client.list_providers()

    providers_filtered = {
        p["code"]: {
            "displayName": p["displayName"],
            "kind": ProviderKind(p["kind"]).name,
        }
        for p in sorted(providers, key=lambda d: d["displayName"])
    }

    return providers_filtered


def parse_args(args: Any) -> Any:
    parser = ArgumentParser(description="awardwallet")

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
    )

    parser.add_argument(
        "--api-key",
        required=True,
        help="API key, can be generated on AwardWallet Business interface",
    )

    sub_parsers = parser.add_subparsers(dest="mode", required=True)

    parser_user_details = sub_parsers.add_parser(
        "user-details", help="Fetch and display details for a specific user"
    )
    parser_user_details.add_argument(
        "--user-id",
        required=True,
        help="User ID for user-specific operations",
    )
    parser_account_details = sub_parsers.add_parser(
        "account-details", help="Fetch and display details for a specific account"
    )
    parser_account_details.add_argument(
        "--account-id",
        required=True,
        help="Account ID for account-specific operations",
    )

    sub_parsers.add_parser("list-providers", help="List all supported providers")
    sub_parsers.add_parser("list-users", help="List all connected users")

    return parser.parse_args(args)


def main(args: Any) -> None:
    args = parse_args(args)

    client = AwardWalletClient(args.api_key)
    resp = []

    if args.mode == "list-providers":
        resp = list_providers(client)
    elif args.mode == "list-users":
        resp = list_users(client)
    elif args.mode == "account-details":
        resp = account_details(client, args.account_id)
    elif args.mode == "user-details":
        resp = user_details(client, args.user_id)

    if resp:
        print(json.dumps(resp, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])

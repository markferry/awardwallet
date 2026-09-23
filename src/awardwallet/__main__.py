import json
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from awardwallet import AwardWalletClient

from . import __version__
from .client import DebugLog

__all__ = ["main"]


def list_users(client):
    connected_users = client.list_connected_users()
    users = {}
    for user in connected_users:
        users[user.user_id] = user.user_name

    return users


def account_details(client, account_id):
    return client.get_account_details(account_id)


def user_details(client, user_id):
    return client.get_connected_user_details(user_id)


def list_providers(client):
    providers = client.list_providers()

    providers_filtered = {
        p.code: {
            "displayName": p.display_name,
            "kind": p.kind.name,
        }
        for p in sorted(providers, key=lambda d: d.display_name)
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

    parser.add_argument(
        "--dump",
        type=Path,
        default=None,
        metavar="FILE",
        help="Append raw API responses as newline-delimited JSON to FILE",
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


def main(argv: list[str] | None = None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    args = parse_args(argv)

    debug_log = DebugLog(args.dump) if args.dump else None
    try:
        _main(args, debug_log)
    finally:
        if debug_log:
            debug_log.close()


def _main(args: Any, debug_log: DebugLog | None) -> None:
    client = AwardWalletClient(args.api_key, debug_log=debug_log)
    resp = []

    if args.mode == "list-providers":
        resp = json.dumps(list_providers(client), indent=2, ensure_ascii=False)
    elif args.mode == "list-users":
        resp = json.dumps(list_users(client), indent=2, ensure_ascii=False)
    elif args.mode == "account-details":
        resp = account_details(client, args.account_id).model_dump_json(indent=2)
    elif args.mode == "user-details":
        resp = user_details(client, args.user_id).model_dump_json(indent=2)

    print(resp)


if __name__ == "__main__":
    main()

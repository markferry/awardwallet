import json
import subprocess
import sys
from unittest.mock import Mock

from awardwallet import __version__
from awardwallet.__main__ import main


def test_cli_version():
    cmd = [sys.executable, "-m", "awardwallet", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__


def test_cli_dump(mocker, tmp_path):
    dump_file = tmp_path / "api.jsonl"
    payload = [{"code": "aa", "displayName": "American Airlines", "kind": 1}]
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = payload
    mocker.patch("requests.Session.request", return_value=mock_response)

    main(["--api-key", "dummy", "--dump", str(dump_file), "list-providers"])

    records = [json.loads(line) for line in dump_file.read_text().splitlines()]
    assert records == [
        {
            "method": "GET",
            "endpoint": "providers/list",
            "status": 200,
            "body": payload,
        }
    ]

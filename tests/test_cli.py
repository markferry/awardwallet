import subprocess
import sys

from awardwallet import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "awardwallet", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__

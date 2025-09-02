"""Top level API.

.. data:: __version__
    :type: str

    Version number as calculated by https://github.com/pypa/setuptools_scm
"""

from ._version import __version__

# API - order matters
# isort: off
from .api import AwardWalletClient

# isort: on

# Help Sphinx document the API
#   https://stackoverflow.com/a/66996523
__all_exports = [
    AwardWalletClient,
]

# Patch imported modules
for e in __all_exports:
    e.__module__ = __name__

__all__ = ["__version__"]
__all__ += [e.__name__ for e in __all_exports]

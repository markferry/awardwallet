[![CI](https://github.com/markferry/awardwallet/actions/workflows/ci.yml/badge.svg)](https://github.com/markferry/awardwallet/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/markferry/awardwallet/branch/main/graph/badge.svg)](https://codecov.io/gh/markferry/awardwallet)
[![PyPI](https://img.shields.io/pypi/v/awardwallet.svg)](https://pypi.org/project/awardwallet)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

# awardwallet

AwardWallet Business API wrapper

This is where you should write a short paragraph that describes what your module does,
how it does it, and why people should use it.

Source          | <https://github.com/markferry/awardwallet>
:---:           | :---:
PyPI            | `pip install awardwallet`
Releases        | <https://github.com/markferry/awardwallet/releases>

This is where you should put some images or code snippets that illustrate
some relevant examples. If it is a library then you might put some
introductory code here:

```python
from awardwallet import AwardWalletClient
import json

api_key = "your_api_key_here"
client = AwardWalletClient(api_key)

print(json.dumps(client.list_providers(), indent=2, ensure_ascii=False))
```

Alternatively use the built in tool:

```
awardwallet --api-key $your_api_key_here list_providers
```
